from typing import Any, Iterable, NamedTuple

from apssm.devices.dc_dc import DcDc
from apssm.devices.diode import Diode
from apssm.devices.power_supply import PowerSupply
from apssm.devices.switch import Switch
from apssm.exceptions import (
    ChargePowerSupply,
    DuplicateConnection,
    DuplicateDevice,
    InvalidPort,
    NoPowerSupplies,
    NoSuchDevice,
)
from apssm.gen_port_id import gen_port_id
from apssm.thin_port import ThinPort
from apssm.tree import AbstractPowerSupplySystemTree, DirectedEdge, DirectedPort
from apssm.typing import DeviceType


class ThinEdge(NamedTuple):
    first: ThinPort
    second: ThinPort
    extras: Any


class Port(NamedTuple):
    device: DeviceType
    index: int
    # list of (node_name, extras)
    adj_list: list[tuple["Port", Any]]

    @property
    def id(self):
        return f"{self.device.name}.{self.index}"


class Edge(NamedTuple):
    first: Port
    second: Port
    extras: Any


class AbstractPowerSupplySystemGraph:
    ports: dict[str, Port]
    devices: dict[str, DeviceType]
    edges: list[Edge]

    def __init__(self):
        self.ports = {}
        self.edges = []
        self.devices = {}

    def add_device(self, device: DeviceType) -> "AbstractPowerSupplySystemGraph":
        if device.name in self.devices:
            raise DuplicateDevice(device.name)
        self.devices[device.name] = device
        for i in range(device.port_num):
            self.ports[gen_port_id(device.name, i)] = Port(device, i, [])
        return self

    def add_edge(
        self,
        first: ThinPort | tuple[str, int],
        second: ThinPort | tuple[str, int],
        extras: Any = None,
    ) -> "AbstractPowerSupplySystemGraph":
        """add edge between port `first` and `second`

        Args:
            first: first port, if it is of type tuple[str, int], it will be
                converted to ThinPort

            second: second port, if it is of type tuple[str, int],
                it will be converted to ThinPort

            extras: extras of edge

        Returns:
            AbstractPowerSupplySystemDag: self

        Throws:
            NoSuchDevice: if device not found
            InvalidPort: if port index is invalid
            DuplicateConnection: if connection already exists
        """
        first_device_name, first_port_index = first
        try:
            first_device = self.devices[first_device_name]
        except KeyError:
            raise NoSuchDevice(first_device_name)
        if first_port_index >= first_device.port_num:
            raise InvalidPort(device=first_device, port_index=first_port_index)

        second_device_name, second_port_index = second
        try:
            second_device = self.devices[second_device_name]
        except KeyError:
            raise NoSuchDevice(second_device_name)

        if second_port_index >= second_device.port_num:
            raise InvalidPort(device=second_device, port_index=second_port_index)

        first_port = self.ports[gen_port_id(first_device_name, first_port_index)]
        second_port = self.ports[gen_port_id(second_device_name, second_port_index)]

        if any(port.id == second_port.id for port, _ in first_port.adj_list):
            raise DuplicateConnection(first, second, extras)

        edge = Edge(first=first_port, second=second_port, extras=extras)
        self.edges.append(edge)

        first_port.adj_list.append((second_port, edge.extras))
        second_port.adj_list.append((first_port, edge.extras))
        return self

    def gen_forest(
        self, truth_table: dict[str, bool] | None = None
    ) -> tuple[AbstractPowerSupplySystemTree, ...]:
        """根据真值表生成森林

            Args:
                truth_table (dict[str, bool] | None, optional): 每个开关对应的开关状态.
        Defaults to None.

            Returns:
                AbstractPowerSupplySystemDag: 当前真值表对应的dag
        """
        if not truth_table:
            truth_table = {}
        for k in truth_table:
            if k not in self.devices:
                raise NoSuchDevice(k)
        directed_roots: list[DirectedPort] = []
        for port in self.ports.values():
            if isinstance(port.device, PowerSupply):
                directed_roots.append(
                    DirectedPort(device=port.device, port_index=port.index)
                )
        if not directed_roots:
            raise NoPowerSupplies()

        forest: list[AbstractPowerSupplySystemTree] = []

        visited_edges: set[str] = set()

        # search from roots
        for directed_root in directed_roots:
            assert isinstance(directed_root.device, PowerSupply)
            stack: list[tuple[DirectedPort, DirectedPort | None]] = [
                (directed_root, None)
            ]
            directed_ports: dict[str, DirectedPort] = {}
            while stack:
                candidate_port, parent_port = stack.pop()
                directed_ports[candidate_port.id] = candidate_port
                # NOTE: 这里必须是一个clone， 因为后面会修改adj_list
                adj_list = self.ports[candidate_port.id].adj_list[:]
                # 若是闭合开关或者dcdc, 视为存在一个到另外一个端口的连接
                is_closed_switch = isinstance(
                    candidate_port.device, Switch
                ) and truth_table.get(
                    candidate_port.device.name, candidate_port.device.on
                )
                is_dc_dc = isinstance(candidate_port.device, DcDc)
                if is_closed_switch or is_dc_dc:
                    the_other_port = self.ports[
                        gen_port_id(
                            candidate_port.device.name,
                            1 - candidate_port.port_index,
                        )
                    ]
                    adj_list.append((the_other_port, None))
                # 若是二极管, 并且是第0端口，视为一个连接

                if (
                    isinstance(candidate_port.device, Diode)
                    and candidate_port.port_index == 0
                ):
                    adj_list.append(
                        (self.ports[gen_port_id(candidate_port.device.name, 1)], None)
                    )
                for port, extras in adj_list:
                    # 防止回溯到父节点
                    if parent_port and port.id == parent_port.id:
                        continue
                    child_port = self.ports[port.id]
                    # 如果找到了一个电源
                    if isinstance(child_port.device, PowerSupply):
                        raise ChargePowerSupply(directed_root.device, child_port.device)

                    directed_child_port = DirectedPort(
                        device=child_port.device, port_index=child_port.index
                    )

                    # 如果是二极管， 并且是第1端口， 停止查找
                    if (
                        not isinstance(candidate_port.device, Diode)
                        and isinstance(directed_child_port.device, Diode)
                        and directed_child_port.port_index == 1
                    ):
                        continue
                    candidate_port.children.append(directed_child_port)
                    directed_child_port.parent = candidate_port
                    directed_edge = DirectedEdge(
                        from_=candidate_port,
                        to=directed_child_port,
                        extras=extras,
                    )
                    visited_edges.add(directed_edge.id)
                    candidate_port.edges.append(directed_edge)

                    stack.append((directed_child_port, candidate_port))
            forest.append(
                AbstractPowerSupplySystemTree(root=directed_root, nodes=directed_ports)
            )

        return tuple(forest)

    def find_passages(
        self,
        destinations: Iterable[tuple[str, int] | ThinPort],
        truth_table: dict[str, bool] | None = None,
    ) -> dict[str, list[tuple[ThinPort, ...]]]:
        """find the passages to the given ports

        **NOTE! 为了防止反复生成森林， 请一次性传入尽可能多的要查找通路的目标端口**

        Args:
            destinations (Iterable[tuple[str, int]  |  ThinPort]): as the name
            truth_table (dict[str, bool] | None, optional): the truth table for switchs.
                Defaults to None.

        Returns:
            dict[str, list[tuple[ThinPort, ...]]]: key is each destination's id,
                value is a list of passages to a give destination


        """
        truth_table = truth_table or {}
        forest = self.gen_forest(truth_table)
        res: dict[str, list[tuple[ThinPort, ...]]] = {}
        for to in destinations:
            if not isinstance(to, ThinPort):
                to = ThinPort(*to)
            for tree in forest:
                if passage := tree.find_passage(to):
                    res.setdefault(to.id, []).append(passage)
        return res
