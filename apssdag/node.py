from typing import Generic, TypeVar

from apssdag.connection import PlainConnection
from apssdag.typings import DeviceType

ND = TypeVar("ND", bound="DeviceType")


class Node(Generic[ND]):
    data: ND
    conns: list[PlainConnection]
    children: list["Node"]

    def __init__(self, data: ND, conns: list[PlainConnection] | None) -> None:
        super().__init__()
        self.data = data
        self.conns = conns or []
        self.children = []
