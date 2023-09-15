from __future__ import annotations

from typing_extensions import Unpack

from .bus import BusData
from .connection import Connection
from .dag import AbstractPowerSupplySystemDag
from .exceptions import NoSuchObject
from .load import LoadData
from .power_supply import PowerSupplyData


class AbstractPowerSupplySystemDagBuilder:
    _create_objects_from_connections: bool
    power_supplies: dict[str, PowerSupplyData]
    buses: dict[str, BusData]
    loads: dict[str, LoadData]
    connections: list[Connection]

    def __init__(self, create_objects_from_connections=False):
        """initialize builder

        Args:
            create_objects_from_connections (bool, optional): 是否从连接关系中自动
                创建对象.  Defaults to False.
        """
        self._create_objects_from_connections = create_objects_from_connections
        self.power_supplies = {}
        self.buses = {}
        self.loads = {}
        self.connections = []

    def add_power_supply(
        self, **kwargs: Unpack[PowerSupplyData]
    ) -> AbstractPowerSupplySystemDagBuilder:
        """添加一个供电
        ```python
        builder.add_power_supply(name="power_supply_1", ...)

        ps = PowerSupplyData(name="power_supply_1", ...)
        builder.add_power_supply(**ps)
        ```

        Returns:
            AbstractPowerSupplySystemDagBuilder: self
        """
        power_supply = PowerSupplyData(kwargs)
        self.power_supplies[power_supply["name"]] = power_supply
        return self

    def add_bus(self, **kwargs: Unpack[BusData]) -> AbstractPowerSupplySystemDagBuilder:
        """添加一个汇流条
        ```python
        builder.add_bus(name="bus1", ...)

        bus = BusData(name="bus1")
        builder.add_bus(**bus)
        ```

        Returns:
            AbstractPowerSupplySystemDagBuilder: self
        """
        bus = BusData(kwargs)
        self.buses[bus["name"]] = bus
        return self

    def add_load(
        self, **kwargs: Unpack[LoadData]
    ) -> AbstractPowerSupplySystemDagBuilder:
        """新增一个负载
        参数是负载属性， 调用方法如下:

        ```python
        builder.add_load(name="load1", ...)

        load = LoadData(name="load1", ...)
        builder.add_load(**load)
        ```

        Returns:
            AbstractPowerSupplySystemDagBuilder: self
        """

        load = LoadData(kwargs)
        self.loads[load["name"]] = load
        return self

    def add_connection(self, conn: Connection) -> AbstractPowerSupplySystemDagBuilder:
        """添加一条连接（即负载统计表记录）

        Args:
            conn (Connection): 被新增的记录

        Raises:
            NoSuchObject: 当不允许从连接中创建对象时, 即not
                create_objects_from_connections , 连接中的汇流条或者负载不存在

        Returns:
            int: 新增记录的id, 从1开始

        """
        if conn.load not in self.loads:
            if not self._create_objects_from_connections:
                raise NoSuchObject(conn.load, type="load")
            self.loads[conn.load] = LoadData(name=conn.load)
        if conn.bus not in self.buses:
            if not self._create_objects_from_connections:
                raise NoSuchObject(conn.bus, type="bus")
            self.buses[conn.bus] = BusData(name=conn.bus)
        self.connections.append(conn)
        return self

    # def build(self) -> AbstractPowerSupplySystemDag:
    #     pass
