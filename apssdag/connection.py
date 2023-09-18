from typing import Any, NamedTuple

from apssdag.typings import DeviceType


class PlainConnection(NamedTuple):
    from_: str
    to: str
    extras: Any


class Connection(NamedTuple):
    from apssdag.node import Node

    from_: Node[DeviceType]
    to: Node[DeviceType]
    extras: Any

    @staticmethod
    def from_plain_conn(plain: PlainConnection, nodes: dict[str, Node[DeviceType]]):
        return Connection(nodes[plain.from_], nodes[plain.to], extras=plain.extras)
