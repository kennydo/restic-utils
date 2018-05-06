import datetime
from unittest import mock

from restic_utils.restic_commands import list_snapshots
from restic_utils.restic_models import Snapshot


@mock.patch('restic_utils.restic_commands.run_command')
def test_list_snapshots_with_host_filter(mock_run_command):
    mock_run_command.return_value = (
        """[
            {
                "time": "2018-04-30T12:30:22.033227319-07:00",
                "parent": "876d720dc0904ce5be20349e8f88040ebbc1d815f4354e0fbd19cc40e8631066",
                "tree": "75a841636e8c4a8fb735d0baf58a5687fb759fb144b54c678156ad714f486dee",
                "paths": [
                    "/home/kedo/Music"
                ],
                "hostname": "kotori",
                "username": "kedo",
                "uid": 1000,
                "gid": 1000,
                "id": "929e9b26c7664bea95187fc3a3a2adf65d834de459e941f88049de9176c72f89",
                "short_id": "929e9b26"
            },
            {
                "time": "2018-05-05T18:06:07.241594457-07:00",
                "tree": "3c8bdfe5f731400c8f5571c4bb75c9aa5517363c204241a5bb1eee2591edbb5d",
                "paths": [
                    "/home/kedo/Documents",
                    "/home/kedo/Music",
                    "/home/kedo/Pictures"
                ],
                "hostname": "kotori",
                "username": "kedo",
                "id": "9840af0abfa94abe9982707a232ed29e045d94ee5e434436943aba33221500c1",
                "short_id": "9840af0a"
            }
        ]""",
        "password is correct",
    )

    snapshots = list_snapshots(only_latest=True, filter_host="kotori")

    assert mock_run_command.call_args_list == [
        mock.call(['restic', 'snapshots', '--json', '--last', '--host', 'kotori']),
    ]

    assert snapshots == [
        Snapshot(
            id_='929e9b26c7664bea95187fc3a3a2adf65d834de459e941f88049de9176c72f89',
            short_id='929e9b26',
            time=datetime.datetime(2018, 4, 30, 19, 30, 22, 33227),
            username='kedo',
            hostname='kotori',
            paths=['/home/kedo/Music'],
            uid=1000,
            gid=1000,
            parent='876d720dc0904ce5be20349e8f88040ebbc1d815f4354e0fbd19cc40e8631066',
            tree='75a841636e8c4a8fb735d0baf58a5687fb759fb144b54c678156ad714f486dee',
        ),
        Snapshot(
            id_='9840af0abfa94abe9982707a232ed29e045d94ee5e434436943aba33221500c1',
            short_id='9840af0a',
            time=datetime.datetime(2018, 5, 6, 1, 6, 7, 241594),
            username='kedo',
            hostname='kotori',
            paths=['/home/kedo/Documents', '/home/kedo/Music', '/home/kedo/Pictures'],
            uid=None,
            gid=None,
            parent=None,
            tree='3c8bdfe5f731400c8f5571c4bb75c9aa5517363c204241a5bb1eee2591edbb5d',
        ),
    ]
