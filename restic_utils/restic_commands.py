import json
import logging
from typing import List
from typing import Optional

from restic_utils import datetimes
from restic_utils import restic_models
from restic_utils.processes import run_command

log = logging.getLogger(__name__)


def list_snapshots(
    *,
    only_latest: bool = False,
    filter_host: Optional[str] = None,
    filter_paths: Optional[List[str]] = None,
    filter_tags: Optional[List[str]] = None,
) -> List[restic_models.Snapshot]:
    """
    :param only_latest: if true, only list the latest snapshots for each host and path
    :param filter_host: if specified, only list snapshots from this host
    :param filter_paths: if specified, only list snapshots that include all of these paths
    :param filter_tags: if specified, only list snapshots that have all of these tags
    """
    cmd = [
        "restic",
        "snapshots",
        "--json",
    ]

    if only_latest:
        cmd.append("--last")

    if filter_host:
        cmd.extend(["--host", filter_host])

    if filter_paths:
        for path in filter_paths:
            cmd.extend(["--path", path])

    if filter_tags:
        for tag in filter_tags:
            cmd.extend(["--tag", tag])

    stdout, _ = run_command(cmd)

    parsed_output = json.loads(stdout)
    log.debug("Parsed %s snapshots entries", len(parsed_output) if parsed_output else "none")

    snapshots = []

    if not parsed_output:
        log.info("Did not parse any entries from snapshots list")
        return snapshots

    for entry in parsed_output:
        snapshots.append(
            restic_models.Snapshot(
                id_=entry["id"],
                short_id=entry["short_id"],
                time=datetimes.parse_iso_8601_to_naive_utc_datetime(entry["time"]),
                username=entry.get("username"),
                hostname=entry["hostname"],
                paths=entry["paths"],
                uid=entry.get("uid"),
                gid=entry.get("gid"),
                parent=entry.get("parent"),
                tree=entry["tree"],
            )
        )

    return snapshots
