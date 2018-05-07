import datetime
import logging
import sys
from datetime import timedelta
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import click

from restic_utils import datetimes
from restic_utils import restic_commands
from restic_utils import restic_models

log = logging.getLogger(__name__)


class HostPath(NamedTuple):
    host: str
    path: str


def parse_host_path_argument(ctx: click.Context, param: click.Parameter, value) -> List[HostPath]:
    if not value:
        raise click.BadParameter("At least one host:/path argument is required")

    host_paths = []

    for entry in value:
        if ':' not in entry:
            raise click.BadParameter(f"Host path was not properly formatted: {entry}")

        elements = entry.split(':', 1)
        host_paths.append(HostPath(host=elements[0], path=elements[1]))

    return host_paths


class SnapshotDB:
    latest_snapshot_ids_by_host_path: Dict[HostPath, str]
    snapshots_by_id: Dict[str, restic_models.Snapshot]

    def __init__(self) -> None:
        self.latest_snapshot_ids_by_host_path = {}
        self.snapshots_by_id = {}

    def fetch_latest_snapshots(self, host_paths: List[HostPath]) -> None:
        unique_hosts = set([host_path.host for host_path in host_paths])
        host_paths_set = set(host_paths)

        for host in unique_hosts:
            snapshots = restic_commands.list_snapshots(only_latest=True, filter_host=host)

            for snapshot in snapshots:
                self.snapshots_by_id[snapshot.id_] = snapshot

                for path in snapshot.paths:
                    key = HostPath(host=host, path=path)

                    if key not in host_paths_set:
                        log.debug("Ignoring snapshot info for %s because it is not a relevant host path", key)
                        continue

                    if key in self.latest_snapshot_ids_by_host_path:
                        # Check whether this snapshot is newer
                        other_snapshot = self.snapshots_by_id[self.latest_snapshot_ids_by_host_path[key]]
                        if snapshot.time > other_snapshot.time:
                            self.latest_snapshot_ids_by_host_path[key] = snapshot.id_
                    else:
                        # We know this is the latest snapshot for this key
                        self.latest_snapshot_ids_by_host_path[key] = snapshot.id_

    def get_latest_snapshot_for_host_path(self, host_path: HostPath) -> Optional[restic_models.Snapshot]:
        if host_path not in self.latest_snapshot_ids_by_host_path:
            return None

        return self.snapshots_by_id[
            self.latest_snapshot_ids_by_host_path[host_path]
        ]


class SnapshotBucketerResult(NamedTuple):
    host_paths_with_recent_snapshots: List[HostPath]
    host_paths_with_old_snapshots: List[HostPath]
    host_paths_with_no_snapshots: List[HostPath]


class SnapshotBucketer:
    snapshot_db: SnapshotDB

    def __init__(self, snapshot_db: SnapshotDB) -> None:
        self.snapshot_db = snapshot_db

    def group_by_snapshot_recency(
        self,
        *,
        host_paths: List[HostPath],
        min_time_bound: datetime.datetime,
    ) -> SnapshotBucketerResult:
        host_paths_with_recent_snapshots = []
        host_paths_with_old_snapshots = []
        host_paths_with_no_snapshots = []

        for key in host_paths:
            if key not in self.snapshot_db.latest_snapshot_ids_by_host_path:
                host_paths_with_no_snapshots.append(key)
                continue

            latest_snapshot = self.snapshot_db.get_latest_snapshot_for_host_path(key)
            assert latest_snapshot

            if latest_snapshot.time > min_time_bound:
                host_paths_with_recent_snapshots.append(key)
            else:
                host_paths_with_old_snapshots.append(key)

        return SnapshotBucketerResult(
            host_paths_with_recent_snapshots=host_paths_with_recent_snapshots,
            host_paths_with_old_snapshots=host_paths_with_old_snapshots,
            host_paths_with_no_snapshots=host_paths_with_no_snapshots,
        )


def _describe_host_path_snapshot(
    snapshot_db: SnapshotDB,
    naive_utc_now: datetime.datetime,
    host_path: HostPath,
) -> str:
    snapshot = snapshot_db.get_latest_snapshot_for_host_path(host_path)
    assert snapshot
    hours = (naive_utc_now - snapshot.time).total_seconds() / (60 * 60)

    return f"{host_path.host}:{host_path.path} snapshot {snapshot.short_id} is {hours:.5} hours old"


@click.command()
@click.option(
    "--max-age-hours",
    default=24 * 7,
    help="Require each directory to have a snapshot no older than this many hours"
)
@click.argument(
    "host_paths",
    nargs=-1,
    callback=parse_host_path_argument,
)
def main(max_age_hours: int, host_paths: List[HostPath]):
    """
    Assert that there exists recent snapshots for the given host/path combinations.
    Returns non-zero exit code if any of the specified host paths do not have a snapshot
    more recent than the max age.

    Specify host paths in hostname:/backed/up/path format.
    """
    naive_utc_now = datetimes.naive_utc_now()
    # The oldest a snapshot can be while still being considered "recent enough" for us
    min_time_bound = naive_utc_now - timedelta(hours=max_age_hours)

    snapshot_db = SnapshotDB()
    snapshot_db.fetch_latest_snapshots(host_paths)

    bucketer = SnapshotBucketer(snapshot_db)
    bucketed_results = bucketer.group_by_snapshot_recency(host_paths=host_paths, min_time_bound=min_time_bound)

    output_groups = [
        "Here are the results of checking for the recency of snapshots for the specified host paths.",
    ]

    if bucketed_results.host_paths_with_recent_snapshots:
        group_lines = ["Host paths with recent snapshots:"]
        group_lines.extend(
            _describe_host_path_snapshot(snapshot_db, naive_utc_now, host_path)
            for host_path in bucketed_results.host_paths_with_recent_snapshots
        )
        output_groups.append("\n".join(group_lines))

    if bucketed_results.host_paths_with_old_snapshots:
        group_lines = ["Host paths with old snapshots:"]
        group_lines.extend(
            _describe_host_path_snapshot(snapshot_db, naive_utc_now, host_path)
            for host_path in bucketed_results.host_paths_with_old_snapshots
        )
        output_groups.append("\n".join(group_lines))

    if bucketed_results.host_paths_with_no_snapshots:
        group_lines = ["Host paths with no snapshots:"]
        group_lines.extend(
            f"{host_path.host}:{host_path.path}"
            for host_path in bucketed_results.host_paths_with_no_snapshots
        )
        output_groups.append("\n".join(group_lines))

    print("\n\n".join(output_groups))

    status_code = 0 if len(bucketed_results.host_paths_with_recent_snapshots) == len(host_paths) else 1
    sys.exit(status_code)


if __name__ == "__main__":
    main()
