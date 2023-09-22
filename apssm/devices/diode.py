from dataclasses import dataclass
from typing import ClassVar, Literal


@dataclass
class Diode:
    """
    A class representing a diode component.

    Attributes:
    -----------
    name : str
        The name of the diode.
    """

    port_num: ClassVar[int] = 2

    name: str
