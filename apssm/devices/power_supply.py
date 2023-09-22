from dataclasses import dataclass
from typing import ClassVar


@dataclass
class PowerSupply:
    port_num: ClassVar[int] = 1

    name: str
