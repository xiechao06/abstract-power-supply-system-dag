from typing import NamedTuple


class Connection(NamedTuple):
    bus: str
    load: str
    redundancy: int
