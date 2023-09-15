from typing import Literal

ObjectType = Literal["bus", "load", "power_supply"]


class NoSuchObject(Exception):
    name: str
    type: ObjectType

    def __init__(self, name: str, /, *, type: ObjectType) -> None:
        super().__init__(f"No such {type}: {name}")
        self.name = name
        self.type = type
