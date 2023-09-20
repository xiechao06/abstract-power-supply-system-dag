from typing import Any, Literal, NamedTuple

from apssdag.typings import DeviceType


class PlainConnection(NamedTuple):
    from_: str
    to: str
    extras: Any


class Connection(NamedTuple):
    """
    Represents a connection between two nodes in the abstract power supply system DAG.
    Note that the direction of the connection is not necessarily from "from_" to "to"

    Attributes:
        from_ (Node[DeviceType]): The node where the connection originates.
        to (Node[DeviceType]): The node where the connection ends.
        extras (Any): Any additional information about the connection.
        direction (Literal["forward", "backward", "unknown"], optional):
            The direction of the connection. Defaults to "unknown".
    """

    from apssdag.node import Node

    from_: Node[DeviceType]
    to: Node[DeviceType]
    extras: Any
    direction: Literal["forward", "backward", "unknown"] = "unknown"

    @staticmethod
    def from_plain_conn(plain: PlainConnection, nodes: dict[str, Node[DeviceType]]):
        return Connection(nodes[plain.from_], nodes[plain.to], extras=plain.extras)
