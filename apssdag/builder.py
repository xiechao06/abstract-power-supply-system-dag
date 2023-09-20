from __future__ import annotations

from typing import Any, cast

from apssdag.dag import AbstractPowerSupplySystemDag
from apssdag.devices.power_supply import PowerSupply
from apssdag.node import Node
from apssdag.typings import DeviceType

from .connection import Connection, PlainConnection
from .exceptions import DuplicateConnection, DuplicateDevice, NoSuchDevice


class AbstractPowerSupplySystemDagBuilder:
    connections: dict[str, list[PlainConnection]]
    devices: dict[str, DeviceType]

    def __init__(self):
        """initialize builder

        Args:
            create_objects_from_connections (bool, optional): 是否从连接关系中自动
                创建对象.  Defaults to False.
        """
        self.devices = {}
        self.connections = {}

    def add_device(self, data: DeviceType) -> AbstractPowerSupplySystemDagBuilder:
        if data.name in self.devices:
            raise DuplicateDevice(data.name)
        self.devices[data.name] = data
        return self

    def add_connection(
        self, *, from_: str, to: str, extras: Any = None
    ) -> AbstractPowerSupplySystemDagBuilder:
        """添加一条连接（即负载统计表记录）

        Args:
            kwargs (Unpack[Connection]): 被新增的记录

        Raises:
            NoSuchObject: 当不允许从连接中创建对象时, 即not
                create_objects_from_connections , 连接中的汇流条或者负载不存在

        Returns:
            AbstractPowerSupplySystemDagBuilder: self

        """
        conn = PlainConnection(from_=from_, to=to, extras=extras)
        if conn.from_ not in self.devices:
            raise NoSuchDevice(conn.from_)
        if conn.to not in self.devices:
            raise NoSuchDevice(conn.to)
        if any(conn.to == conn_.to for conn_ in self.connections.get(conn.from_, [])):
            raise DuplicateConnection(from_=conn.from_, to=conn.to, extras=conn.extras)
        self.connections.setdefault(conn.from_, []).append(conn)
        return self

    def build(self) -> AbstractPowerSupplySystemDag:
        dag = AbstractPowerSupplySystemDag()
        for device_data in self.devices.values():
            conns = self.connections.get(device_data.name)
            node = Node[type(device_data)](device_data, conns)
            if isinstance(device_data, PowerSupply):
                dag.roots.append(cast(Node[PowerSupply], node))
            dag.nodes[node.data.name] = node
        # set children
        for node in dag.nodes.values():
            for conn in node.conns:
                node.children.append(dag.nodes[conn.to])
        for from_ in self.connections:
            dag.conns[from_] = list(
                Connection.from_plain_conn(conn, dag.nodes)
                for conn in self.connections[from_]
            )

        return dag
