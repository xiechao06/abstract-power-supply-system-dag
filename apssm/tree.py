from dataclasses import dataclass
from typing import Any, NamedTuple, TypeVar

from apssm.devices.bus import Bus
from apssm.devices.dc_dc import DcDc
from apssm.devices.diode import Diode
from apssm.devices.load import Load
from apssm.devices.power_supply import PowerSupply
from apssm.devices.switch import Switch
from apssm.typing import DeviceType

PathType = list[str]

NT = TypeVar("NT", PowerSupply, Switch, DcDc, Bus, Load, Diode)


class DirectedPort:
    device: DeviceType
    port_index: int
    edges: list["DirectedEdge"]
    children: list["DirectedPort"]

    def __init__(
        self,
        device: DeviceType,
        port_index: int,
    ) -> None:
        super().__init__()
        self.device = device
        self.port_index = port_index
        self.edges = []
        self.children = []

    @property
    def id(self) -> str:
        from apssm.gen_port_id import gen_port_id

        return gen_port_id(self.device.name, self.port_index)


class DirectedEdge(NamedTuple):
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

    from_: DirectedPort
    to: DirectedPort
    extras: Any

    @property
    def id(self):
        return f"{self.from_.device.name} -> {self.to.device.name}"

    @staticmethod
    def gen_edge_id(from_: str, to: str):
        return f"{from_} -> {to}"


@dataclass
class AbstractPowerSupplySystemTree:
    root: DirectedPort
    # nodes: dict[str, DirectedNode]

    def find_paths(self, to: str) -> tuple[PathType]:
        pass
