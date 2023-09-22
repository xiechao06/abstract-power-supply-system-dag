from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Load:
    """
    负载数据
    """

    port_num: ClassVar[int] = 1
    name: str
