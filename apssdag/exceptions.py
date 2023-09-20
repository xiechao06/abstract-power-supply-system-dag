from typing import Any


class NoSuchDevice(Exception):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__(f"No such Device: {name}")
        self.name = name


class DuplicateDevice(Exception):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__(f"Duplicate Device: {name}")
        self.name = name


class DuplicateConnection(Exception):
    from_: str
    to: str
    extras: Any

    def __init__(self, from_: str, to: str, extras: Any = None):
        self.from_ = from_
        self.to = to
        self.extras = extras
        super().__init__(
            f"Duplicate connection: from {self.from_} to {self.to},"
            f" extras - {self.extras}"
        )
