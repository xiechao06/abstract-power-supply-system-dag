from __future__ import annotations
from .connection import Connection
from .exceptions import NoSuchObject
from .load import Load
from .power_supply import PowerSupply
from .bus import Bus


class AbstractPowerSupplySystemBuilder:
    _create_objects_from_connections: bool
    power_supplies: dict[str, PowerSupply]
    buses: dict[str, Bus]
    loads: dict[str, Load]
    connections: list[Connection]

    def __init__(self, create_objects_from_connections=False):
        """initialize builder

        Args:
            create_objects_from_connections (bool, optional): 是否从连接关系中自动创建对象. Defaults to False.
        """
        self._create_objects_from_connections = create_objects_from_connections
        self.power_supplies = {}
        self.buses = {}
        self.loads = {}
        self.connections = []

    def add_power_supply(
        self, power_supply: PowerSupply
    ) -> AbstractPowerSupplySystemBuilder:
        """添加一个供电

        Args:
            power_supply (PowerSupply): 被新增的供电
        """
        self.power_supplies[power_supply.name] = power_supply
        return self

    def add_bus(self, bus: Bus) -> AbstractPowerSupplySystemBuilder:
        """添加一个汇流条

        Args:
            bus (Bus): 被新增的汇流条
        """
        self.buses[bus.name] = bus
        return self

    def add_load(self, load: Load) -> AbstractPowerSupplySystemBuilder:
        """添加一个负载

        Args:
            load (Load): 被新增的负载
        """
        self.loads[load.name] = load
        return self

    def add_connection(self, conn: Connection) -> AbstractPowerSupplySystemBuilder:
        """添加一条连接（即负载统计表记录）

        Args:
            conn (Connection): 被新增的记录

        Raises:
            NoSuchObject: 当不允许从连接中创建对象时(not create_objects_from_connections), 连接中的汇流条或者负载不存在

        Returns:
            int: 新增记录的id, 从1开始

        """
        if conn.load not in self.loads:
            if not self._create_objects_from_connections:
                raise NoSuchObject(conn.load, type="load")
            self.loads[conn.load] = Load(name=conn.load)
        if conn.bus not in self.buses:
            if not self._create_objects_from_connections:
                raise NoSuchObject(conn.bus, type="bus")
            self.buses[conn.bus] = Bus(name=conn.bus)
        self.connections.append(conn)
        return self
