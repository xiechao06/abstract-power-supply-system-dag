from typing import Generic, TypeVar

from apssdag.connection import Connection
from apssdag.typings import DeviceType

ND = TypeVar("ND", bound="DeviceType")


class Node(Generic[ND]):
    data: ND
    conns: list[Connection]
    children: list["Node"]

    def __init__(self, data: ND, conns: list[Connection] | None) -> None:
        super().__init__()
        self.data = data
        self.conns = conns or []
        self.children = []
