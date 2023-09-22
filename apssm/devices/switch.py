from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Switch:
    port_num: ClassVar[int] = 2

    name: str
    on: bool = True

    def turn_on(self):
        self.on = True

    def turn_off(self):
        self.on = False
