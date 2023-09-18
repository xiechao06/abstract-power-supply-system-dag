import pytest

from apssdag.builder import AbstractPowerSupplySystemDagBuilder
from apssdag.devices.bus import Bus
from apssdag.devices.dc_dc_converter import DcDc
from apssdag.devices.load import Load
from apssdag.devices.power_supply import PowerSupply
from apssdag.devices.switch import Switch
from apssdag.exceptions import DuplicateDevice, NoSuchDevice
from apssdag.node import Node


class TestBuilder:
    def test_add_connection(self):
        builder = (
            AbstractPowerSupplySystemDagBuilder()
            .add_device(Bus(name="bus1"))
            .add_device(Load(name="load1"))
        )

        with pytest.raises(DuplicateDevice) as e:
            builder.add_device(Bus(name="bus1"))
        assert e.value.name == "bus1"

        with pytest.raises(NoSuchDevice) as e:
            builder.add_connection(
                from_="nonexistent_bus", to="load1", extras={"redundancy": 1}
            )
        assert e.value.name == "nonexistent_bus"

        with pytest.raises(NoSuchDevice) as e:
            builder.add_connection(
                from_="bus1", to="nonexistent_load", extras={"redundancy": 1}
            )
        assert e.value.name == "nonexistent_load"

        builder.add_connection(from_="bus1", to="load1", extras={"redundancy": 1})

    def test_build(self):
        builder = AbstractPowerSupplySystemDagBuilder()

        builder.add_device(PowerSupply(name="power_supply_1"))

        builder.add_device(Switch(name="switch_1"))
        builder.add_connection(from_="power_supply_1", to="switch_1")

        builder.add_device(DcDc(name="dc_dc_1"))
        builder.add_connection(from_="switch_1", to="dc_dc_1")

        builder.add_device(Bus(name="bus_1"))
        builder.add_connection(from_="dc_dc_1", to="bus_1")

        builder.add_device(Switch(name="switch_2"))
        builder.add_connection(from_="bus_1", to="switch_2")

        builder.add_device(Load(name="load_1"))
        builder.add_connection(from_="switch_2", to="load_1")

        dag = builder.build()
        assert len(dag.roots) == 1

        assert "power_supply_1" in dag.devices

        def assert_0_0(root: Node[PowerSupply]):
            assert root.data.name == "power_supply_1"
            assert len(root.conns) == 1
            assert len(root.children) == 1

            def assert_1_0(node: Node[Switch]):
                assert node.data.name == "switch_1"
                assert len(node.children) == 1

                def assert_2_0(node: Node[DcDc]):
                    assert node.data.name == "dc_dc_1"
                    assert len(node.children) == 1

                    def assert_3_0(node: Node[Bus]):
                        assert node.data.name == "bus_1"
                        assert len(node.children) == 1

                        def assert_4_0(node: Node[Switch]):
                            assert node.data.name == "switch_2"
                            assert len(node.children) == 1

                            def assert_5_0(node: Node[Load]):
                                assert node.data.name == "load_1"
                                assert len(node.children) == 0

                            assert_5_0(node.children[0])

                        assert_4_0(node.children[0])

                    assert_3_0(node.children[0])

                assert_2_0(node.children[0])

            assert_1_0(root.children[0])

        assert_0_0(dag.roots[0])
