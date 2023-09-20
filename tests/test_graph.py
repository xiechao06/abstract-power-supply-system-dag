# -*- coding: utf-8 -*-


import pytest

from apssdag.devices.power_supply import PowerSupply
from apssdag.devices.switch import Switch
from apssdag.exceptions import DuplicateDevice, NoSuchDevice
from apssdag.graph import AbstractPowerSupplySystemGraph


def test_add_device():
    graph = AbstractPowerSupplySystemGraph()
    graph.add_device(PowerSupply("power_supply_1"))
    with pytest.raises(DuplicateDevice) as e:
        graph.add_device(PowerSupply("power_supply_1"))
    assert e.value.name == "power_supply_1"
    assert e.value.name == "power_supply_1"


def test_add_edge():
    graph = AbstractPowerSupplySystemGraph()
    graph.add_device(PowerSupply("power_supply_1"))
    graph.add_device(Switch("switch_1"))
    with pytest.raises(NoSuchDevice) as e:
        graph.add_edge(from_="power_supply_1", to="nonexistent_switch")
    assert e.value.name == "nonexistent_switch"
    with pytest.raises(NoSuchDevice) as e:
        graph.add_edge(from_="nonexistent_powser_supply", to="switch_1")
    assert e.value.name == "nonexistent_powser_supply"

    graph.add_edge(from_="power_supply_1", to="switch_1", extras="foo")

    from_ = graph.nodes["power_supply_1"]
    to = graph.nodes["switch_1"]
    assert len(from_.adj_list) == 1
    assert len(to.adj_list) == 1
    assert from_.adj_list[0][0] == "switch_1"
    assert to.adj_list[0][0] == "power_supply_1"


# def test_as_dag():
#     graph = AbstractPowerSupplySystemGraph()
#     graph.add_device(PowerSupply("power_supply_1"))
#     dag = graph.as_dag()
#     assert len(dag.roots) == 1
