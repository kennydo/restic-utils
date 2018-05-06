import datetime
from typing import List
from typing import NamedTuple
from typing import Optional


class Snapshot(NamedTuple):
    id_: str
    short_id: str
    time: datetime.datetime
    username: Optional[str]
    hostname: str
    paths: List[str]
    uid: Optional[int]
    gid: Optional[int]
    parent: Optional[str]
    tree: str
