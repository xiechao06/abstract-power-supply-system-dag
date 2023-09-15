import pytest

from apssdag import AbstractPowerSupplySystemDagBuilder, Connection
from apssdag.exceptions import NoSuchObject


class TestBuilder:
    def test_add_connection_1(self):
        builder = (
            AbstractPowerSupplySystemDagBuilder()
            .add_bus(name="bus1")
            .add_load(name="load1")
        )

        with pytest.raises(NoSuchObject) as e:
            conn = Connection(bus="nonexistent_bus", load="load1", redundancy=1)
            builder.add_connection(conn)
        assert e.value.name == "nonexistent_bus"
        assert e.value.type == "bus"

        with pytest.raises(NoSuchObject) as e:
            conn = Connection(bus="bus1", load="nonexistent_load", redundancy=1)
            builder.add_connection(conn)
        assert e.value.name == "nonexistent_load"
        assert e.value.type == "load"

        conn = Connection(bus="bus1", load="load1", redundancy=1)
        builder.add_connection(conn)

    def test_add_connection_2(self):
        builder = AbstractPowerSupplySystemDagBuilder(
            create_objects_from_connections=True
        )

        conn = Connection(bus="bus1", load="load1", redundancy=1)
        builder.add_connection(conn)

        assert "bus1" in builder.buses
        assert "load1" in builder.loads
