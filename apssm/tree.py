from dataclasses import dataclass
from typing import Any, NamedTuple, Optional, TypeVar

from loguru import logger

from apssm.devices.bus import Bus
from apssm.devices.dc_dc import DcDc
from apssm.devices.diode import Diode
from apssm.devices.load import Load
from apssm.devices.power_supply import PowerSupply
from apssm.devices.switch import Switch
from apssm.thin_port import ThinPort
from apssm.typing import DeviceType

NT = TypeVar("NT", PowerSupply, Switch, DcDc, Bus, Load, Diode)


class DirectedPort:
    device: DeviceType
    port_index: int
    edges: list["DirectedEdge"]
    children: list["DirectedPort"]
    parent: Optional["DirectedPort"]

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
        self.parent = None

    @property
    def id(self) -> str:
        from apssm.gen_port_id import gen_port_id

        return gen_port_id(self.device.name, self.port_index)

    def as_thin_port(self) -> ThinPort:
        return ThinPort(self.device.name, self.port_index)


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
    nodes: dict[str, DirectedPort]

    def find_passage(self, to: ThinPort) -> tuple[ThinPort, ...] | None:
        """
        Finds the passage from the root of the tree to the given ThinPort.

        Args:
            to (ThinPort): The ThinPort to find the passage to.

        Returns:
            tuple[ThinPort, ...] | None: A tuple of ThinPorts representing the passage
                from the root to the given ThinPort, or None if there is no path to
                the given ThinPort.
        """
        try:
            node = self.nodes[to.id]
        except KeyError:
            logger.debug(f"no such port {to.id} in tree(root: {self.root.id})")
            # no path to `to`
            return
        path: list[ThinPort] = [node.as_thin_port()]
        while node := node.parent:
            path.append(node.as_thin_port())
        return tuple(reversed(path))
