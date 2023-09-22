from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Bus:
    # bus可以认为只有一个端口
    port_num: ClassVar[int] = 1

    name: str
