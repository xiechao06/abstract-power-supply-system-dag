from dataclasses import dataclass


@dataclass
class Switch:
    name: str
    on: bool = True
