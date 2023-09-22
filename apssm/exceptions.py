from typing import Any

from apssm.devices.power_supply import PowerSupply
from apssm.thin_port import ThinPort
from apssm.typing import DeviceType


class NoSuchDevice(Exception):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__(f"No such Device: {name}")
        self.name = name


class DuplicateDevice(Exception):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__(f"Duplicate Device: {name}")
        self.name = name


class DuplicateConnection(Exception):
    from_: ThinPort
    to: ThinPort
    extras: Any

    def __init__(
        self,
        from_: ThinPort | tuple[str, int],
        to: ThinPort | tuple[str, int],
        extras: Any = None,
    ):
        self.from_ = from_ if isinstance(from_, ThinPort) else ThinPort(*from_)
        self.to = to if isinstance(to, ThinPort) else ThinPort(*to)
        self.extras = extras
        super().__init__(
            f"Duplicate connection: from {self.from_} to {self.to},"
            f" extras - {self.extras}"
        )


class NoPowerSupplies(Exception):
    """
    Exception raised when there are no power supplies in the graph.
    """

    def __init__(self):
        super().__init__("No power supplies in graph")


class ChargePowerSupply(Exception):
    """
    Exception raised when attempting to charge a power supply.

    Attributes:
        from_ (PowerSupply): The power supply being charged from.
        to (PowerSupply): The power supply being charged to.
    """

    from_: PowerSupply
    to: PowerSupply

    def __init__(self, from_: PowerSupply, to: PowerSupply):
        super().__init__(f"Charge power supply: from {from_.name} to {to.name}")
        self.from_ = from_
        self.to = to


class FoundCircle(Exception):
    """
    Exception raised when a circular dependency is found in the abstract power supply system DAG.

    Attributes:
        first (str): The name of the first node in the circular dependency.
        end (str): The name of the last node in the circular dependency.
    """

    first: str
    end: str

    def __init__(self, first: str, end: str):
        super().__init__(f"Found circular: from {first} to {end}")
        self.first = first
        self.end = end


class InvalidPort(Exception):
    device: DeviceType
    port_index: int

    def __init__(self, device: DeviceType, port_index: int):
        super().__init__(f"Invalid port: {device.name}.{port_index}")
        self.device = device
        self.port_index = port_index
