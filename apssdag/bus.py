from typing import TypedDict


class Bus:
    _name: str

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
        # TODO propogate to connections


class BusData(TypedDict):
    name: str
