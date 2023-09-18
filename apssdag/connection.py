from typing import Any, NamedTuple


class Connection(NamedTuple):
    from_: str
    to: str
    extras: Any
