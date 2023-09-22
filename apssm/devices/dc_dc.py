from dataclasses import dataclass
from typing import ClassVar


@dataclass
class DcDc:
    port_num: ClassVar[int] = 2

    name: str
