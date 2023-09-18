from apssdag.connection import Connection


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
    value: Connection

    def __init__(self, conn: Connection):
        super().__init__(
            f"Duplicate connection: from {conn.from_} to {conn.to},"
            f" extras - {conn.extras}"
        )
        self.value = conn
