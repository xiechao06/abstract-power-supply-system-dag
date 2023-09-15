from typing import TypedDict


class PowerSupply:
    _name: str

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        # TODO: propogate to connections


class PowerSupplyData(TypedDict):
    name: str
