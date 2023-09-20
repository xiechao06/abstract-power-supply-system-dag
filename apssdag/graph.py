from dataclasses import dataclass
from typing import Any

from apssdag.exceptions import DuplicateConnection, DuplicateDevice, NoSuchDevice
from apssdag.typings import DeviceType


@dataclass
class Edge:
    from_: str
    to: str
    extras: Any


@dataclass
class _Node:
    device: DeviceType
    # list of (node_name, Edge)
    adj_list: list[tuple[str, Edge]]


class AbstractPowerSupplySystemGraph:
    nodes: dict[str, _Node]

    def __init__(self):
        self.nodes = {}

    def add_device(self, device: DeviceType):
        if device.name in self.nodes:
            raise DuplicateDevice(device.name)
        self.nodes[device.name] = _Node(device, [])

    def add_edge(self, from_: str, to: str, extras: Any = None):
        try:
            from_device = self.nodes[from_]
        except KeyError:
            raise NoSuchDevice(from_)
        try:
            to_device = self.nodes[to]
        except KeyError:
            raise NoSuchDevice(to)

        if any(node_name == to for node_name, _ in from_device.adj_list):
            raise DuplicateConnection(from_, to, extras)

        edge = Edge(from_, to, extras)

        from_device.adj_list.append((to, edge))
        to_device.adj_list.append((from_, edge))

    # def as_dag(
    #     self, truth_table: dict[str, bool] | None = None
    # ) -> AbstractPowerSupplySystemDag:
    #     """根据真值表生成dag

    #     Args:
    #         truth_table (dict[str, bool] | None, optional): 每个开关对应的开关状态.
    # Defaults to None.

    #     Returns:
    #         AbstractPowerSupplySystemDag: 当前真值表对应的dag
    #     """
    #     pass
