# -*- coding: utf-8 -*-


from typing import cast

import pytest

from apssm.devices.bus import Bus
from apssm.devices.dc_dc import DcDc
from apssm.devices.diode import Diode
from apssm.devices.load import Load
from apssm.devices.power_supply import PowerSupply
from apssm.devices.switch import Switch
from apssm.exceptions import (
    ChargePowerSupply,
    DuplicateConnection,
    DuplicateDevice,
    InvalidPort,
    NoPowerSupplies,
    NoSuchDevice,
)
from apssm.gen_port_id import gen_port_id
from apssm.graph import AbstractPowerSupplySystemGraph
from apssm.thin_port import ThinPort
from apssm.tree import DirectedPort


def test_add_device():
    graph = AbstractPowerSupplySystemGraph()
    graph.add_device(PowerSupply("power_supply_1"))
    with pytest.raises(DuplicateDevice) as e:
        graph.add_device(PowerSupply("power_supply_1"))
    assert e.value.name == "power_supply_1"
    assert e.value.name == "power_supply_1"


def test_add_edge():
    graph = AbstractPowerSupplySystemGraph()
    graph.add_device(PowerSupply("power_supply"))
    graph.add_device(Switch("switch"))
    with pytest.raises(NoSuchDevice) as e:
        graph.add_edge(
            first=ThinPort("power_supply", 0), second=ThinPort("nonexistent_switch", 0)
        )
    assert e.value.name == "nonexistent_switch"
    with pytest.raises(NoSuchDevice) as e:
        graph.add_edge(
            first=ThinPort("nonexistent_powser_supply", 0), second=ThinPort("switch", 0)
        )
    assert e.value.name == "nonexistent_powser_supply"

    with pytest.raises(InvalidPort) as e:
        graph.add_edge(first=("power_supply", 1), second=("switch", 0))
    assert e.value.device.name == "power_supply" and e.value.port_index == 1

    graph.add_edge(first=("power_supply", 0), second=("switch", 0), extras="foo")

    from_ = graph.ports[gen_port_id("power_supply", 0)]
    to = graph.ports[gen_port_id("switch", 0)]
    assert len(from_.adj_list) == 1
    assert len(to.adj_list) == 1
    assert from_.adj_list[0][0] == to
    assert to.adj_list[0][0] == from_
    with pytest.raises(DuplicateConnection) as e:
        graph.add_edge(first=("power_supply", 0), second=("switch", 0), extras="foo")
    assert e.value.from_.device_name == "power_supply" and e.value.from_.index == 0
    assert e.value.to.device_name == "switch" and e.value.to.index == 0


def test_gen_forest_1():
    graph = AbstractPowerSupplySystemGraph()
    with pytest.raises(NoPowerSupplies):
        graph.gen_forest()


def test_gen_forest_2():
    graph = AbstractPowerSupplySystemGraph()
    power_supply_1 = PowerSupply("power_supply_1")
    graph.add_device(power_supply_1)
    forest = graph.gen_forest()
    assert len(forest) == 1
    root = forest[0].root
    assert root.device == power_supply_1
    assert root.port_index == 0
    assert len(forest[0].nodes) == 1
    assert "power_supply_1.0" in forest[0].nodes

    power_supply_2 = PowerSupply("power_supply_2")
    graph.add_device(power_supply_2)
    forest = graph.gen_forest()
    assert len(forest) == 2

    tree1, tree2 = forest

    root1 = tree1.root
    assert root1.device == power_supply_1
    assert root1.port_index == 0
    assert len(tree1.nodes) == 1
    assert "power_supply_1.0" in tree1.nodes
    assert not root1.parent

    root2 = tree2.root
    assert root2.port_index == 0
    assert "power_supply_2.0" in tree2.nodes
    assert not root2.parent


def test_gen_forest_3():
    graph = AbstractPowerSupplySystemGraph()
    power_supply_1 = PowerSupply("power_supply_1")
    graph.add_device(power_supply_1)

    power_supply_2 = PowerSupply("power_supply_2")
    graph.add_device(power_supply_2).add_edge(
        ("power_supply_1", 0), ("power_supply_2", 0)
    )

    with pytest.raises(ChargePowerSupply) as e:
        graph.gen_forest()

    assert e.value.from_ == power_supply_1 and e.value.to == power_supply_2


def test_gen_forest_4():
    graph = AbstractPowerSupplySystemGraph()
    power_supply_1 = PowerSupply("power_supply_1")
    graph.add_device(power_supply_1)

    switch = Switch("switch", on=True)
    graph.add_device(switch).add_edge(("power_supply_1", 0), ("switch", 0))

    power_supply_2 = PowerSupply("power_supply_2")
    graph.add_device(power_supply_2).add_edge(("switch", 1), ("power_supply_2", 0))

    with pytest.raises(ChargePowerSupply) as e:
        graph.gen_forest()

    assert e.value.from_ == power_supply_1 and e.value.to == power_supply_2

    switch.turn_off()

    forest = graph.gen_forest()
    assert len(forest) == 2

    tree1, tree2 = forest

    assert len(tree1.nodes) == 2
    assert "power_supply_1.0" in tree1.nodes and "switch.0" in tree1.nodes
    assert tree1.root.device == power_supply_1
    assert len(tree1.root.children) == 1
    child = tree1.root.children[0]
    assert not child.children
    assert child.device == switch
    assert child.port_index == 0
    assert child.parent == tree1.root

    assert len(tree2.nodes) == 2
    assert "power_supply_2.0" in tree2.nodes and "switch.1" in tree2.nodes
    assert tree2.root.device == power_supply_2
    assert len(tree2.root.children) == 1
    child = tree2.root.children[0]
    assert not child.children
    assert child.device == switch and child.port_index == 1
    assert child.parent == tree2.root


def test_gen_forest_5():
    graph = AbstractPowerSupplySystemGraph()
    power_supply_0 = PowerSupply("power_supply_0")
    graph.add_device(power_supply_0)

    diode_0 = Diode("diode_0")
    graph.add_device(diode_0).add_edge(("power_supply_0", 0), ("diode_0", 0))

    bus = Bus("bus")
    graph.add_device(bus).add_edge(("diode_0", 1), ("bus", 0))

    load = Load("load")
    graph.add_device(load).add_edge(("bus", 0), ("load", 0))

    power_supply_1 = PowerSupply("power_supply_1")
    graph.add_device(power_supply_1)

    diode_1 = Diode("diode_1")
    graph.add_device(diode_1).add_edge(("power_supply_1", 0), ("diode_1", 0))

    graph.add_edge(("diode_1", 1), ("bus", 0))

    forest = graph.gen_forest()

    assert (len(forest)) == 2

    tree_0, tree_1 = forest

    assert len(tree_0.nodes) == 5
    for name in ("power_supply_0.0", "diode_0.0", "diode_0.1", "bus.0", "load.0"):
        assert name in tree_0.nodes

    assert len(tree_1.nodes) == 5
    for name in ("power_supply_1.0", "diode_1.0", "diode_1.1", "bus.0", "load.0"):
        assert name in tree_1.nodes

    def assert_tree_0(root: DirectedPort):
        assert root.device == power_supply_0
        assert len(root.children) == 1
        _0 = root.children[0]
        assert _0.device == diode_0
        assert len(_0.children) == 1
        _0_0 = _0.children[0]
        assert _0_0.device == diode_0
        assert _0_0.port_index == 1

        _0_0_0 = _0_0.children[0]
        assert _0_0_0.device == bus
        assert _0_0_0.port_index == 0
        assert len(_0_0_0.children) == 1

        _0_0_0_0 = _0_0_0.children[0]
        assert _0_0_0_0.device == load
        assert _0_0_0_0.port_index == 0
        assert not _0_0_0_0.children

    assert_tree_0(tree_0.root)

    def assert_tree_1(root: DirectedPort):
        assert root.device == power_supply_1
        assert len(root.children) == 1
        _0 = root.children[0]

        assert _0.device == diode_1
        assert len(_0.children) == 1

        _0_0 = _0.children[0]
        assert _0_0.device == diode_1
        assert len(_0_0.children) == 1

        _0_0_0 = _0_0.children[0]
        assert _0_0_0.device == bus
        assert _0_0_0.port_index == 0
        assert len(_0_0_0.children) == 1

        _0_0_0_0 = _0_0_0.children[0]
        assert _0_0_0_0.device == load
        assert _0_0_0_0.port_index == 0
        assert not _0_0_0_0.children

    assert_tree_1(tree_1.root)


@pytest.fixture
def graph_fixture():
    graph = AbstractPowerSupplySystemGraph()
    power_supply_0 = PowerSupply("power_supply_0")
    power_supply_1 = PowerSupply("power_supply_1")
    graph.add_device(power_supply_0).add_device(power_supply_1)

    switch_0 = Switch("switch_0", on=True)
    switch_1 = Switch("switch_1", on=True)
    graph.add_device(switch_0).add_edge(("power_supply_0", 0), ("switch_0", 0))
    graph.add_device(switch_1).add_edge(("power_supply_1", 0), ("switch_1", 0))

    bus_0 = Bus("bus_0")
    bus_1 = Bus("bus_1")
    graph.add_device(bus_0).add_edge(("switch_0", 1), ("bus_0", 0))
    graph.add_device(bus_1).add_edge(("switch_1", 1), ("bus_1", 0))

    switch_2 = Switch("switch_2")
    graph.add_device(switch_2)
    graph.add_edge(("bus_0", 0), ("switch_2", 0)).add_edge(
        ("bus_1", 0), ("switch_2", 1)
    )

    load_0 = Load("load_0")
    load_1 = Load("load_1")
    graph.add_device(load_0).add_edge(("bus_0", 0), ("load_0", 0))
    graph.add_device(load_1).add_edge(("bus_1", 0), ("load_1", 0))
    return graph


def test_gen_forest_6(graph_fixture: AbstractPowerSupplySystemGraph):
    graph = graph_fixture
    devices = graph.devices
    with pytest.raises(ChargePowerSupply) as e:
        graph.gen_forest()
    assert (
        e.value.from_ == devices["power_supply_0"]
        and e.value.to == devices["power_supply_1"]
    )


def test_gen_forest_7(graph_fixture: AbstractPowerSupplySystemGraph):
    graph = graph_fixture
    D = graph.devices

    cast(Switch, D["switch_0"]).turn_on()
    cast(Switch, D["switch_1"]).turn_on()
    cast(Switch, D["switch_2"]).turn_off()

    forest = graph.gen_forest()
    assert len(forest) == 2

    tree_0, tree_1 = forest
    assert len(tree_0.nodes) == 6
    for name in (
        "power_supply_0.0",
        "switch_0.0",
        "switch_0.1",
        "bus_0.0",
        "switch_2.0",
        "load_0.0",
    ):
        assert name in tree_0.nodes

    assert len(tree_1.nodes) == 6
    for name in (
        "power_supply_1.0",
        "switch_1.0",
        "switch_1.1",
        "bus_1.0",
        "switch_2.1",
        "load_1.0",
    ):
        assert name in tree_1.nodes

    _0, _1 = tuple(t.root for t in forest)

    assert _0.device == D["power_supply_0"] and _0.port_index == 0
    assert len(_0.children) == 1
    assert not _0.parent
    _00 = _0.children[0]
    assert _00.device == D["switch_0"] and _00.port_index == 0
    assert len(_00.children) == 1
    assert _00.parent == _0

    _000 = _00.children[0]
    assert _000.device == D["switch_0"] and _000.port_index == 1
    assert len(_000.children) == 1
    assert _000.parent == _00

    _0000 = _000.children[0]
    assert _0000.device == D["bus_0"] and _0000.port_index == 0
    assert len(_0000.children) == 2
    assert _0000.parent == _000

    _00000, _00001 = _0000.children
    assert _00001.device == D["load_0"] and _00001.port_index == 0
    assert not _00001.children
    assert _00001.parent == _0000

    assert _00000.device == D["switch_2"] and _00000.port_index == 0
    assert not _00000.children
    assert _00000.parent == _0000

    assert _1.device == D["power_supply_1"] and _1.port_index == 0
    assert len(_1.children) == 1
    assert not _1.parent

    _10 = _1.children[0]
    assert _10.device == D["switch_1"] and _10.port_index == 0
    assert len(_10.children) == 1
    assert _10.parent == _1

    _100 = _10.children[0]
    assert _100.device == D["switch_1"] and _100.port_index == 1
    assert len(_100.children) == 1
    assert _100.parent == _10

    _1000 = _100.children[0]
    assert _1000.device == D["bus_1"] and _1000.port_index == 0
    assert len(_1000.children) == 2
    assert _1000.parent == _100

    _10000, _10001 = _1000.children

    assert _10000.device == D["switch_2"] and _10000.port_index == 1
    assert not len(_10000.children)
    assert _10000.parent == _1000

    assert _10001.device == D["load_1"] and _10001.port_index == 0
    assert not len(_10001.children)
    assert _10001.parent == _1000


def test_gen_forest_8(graph_fixture: AbstractPowerSupplySystemGraph):
    graph = graph_fixture
    D = graph.devices

    cast(Switch, D["switch_0"]).turn_off()
    cast(Switch, D["switch_1"]).turn_on()
    cast(Switch, D["switch_2"]).turn_on()

    forest = graph.gen_forest()
    assert len(forest) == 2

    tree_0, tree_1 = forest

    assert len(tree_0.nodes) == 2

    for name in (
        "power_supply_0.0",
        "switch_0.0",
    ):
        assert name in tree_0.nodes

    assert len(tree_1.nodes) == 10

    for name in (
        "power_supply_1.0",
        "switch_1.0",
        "switch_1.1",
        "bus_1.0",
        "switch_2.0",
        "switch_2.1",
        "bus_0.0",
        "switch_0.1",
        "load_0.0",
        "load_1.0",
    ):
        assert name in tree_1.nodes

    _0, _1 = (t.root for t in forest)

    assert _0.device == D["power_supply_0"] and _0.port_index == 0
    _00 = _0.children[0]
    assert _00.device == D["switch_0"] and _00.port_index == 0
    assert not _00.children

    assert _1.device == D["power_supply_1"] and _1.port_index == 0
    _10 = _1.children[0]
    assert _10.device == D["switch_1"] and _10.port_index == 0
    assert len(_10.children) == 1

    _100 = _10.children[0]
    assert _100.device == D["switch_1"] and _100.port_index == 1
    assert len(_100.children) == 1

    _1000 = _100.children[0]
    assert _1000.device == D["bus_1"] and _1000.port_index == 0
    assert len(_1000.children) == 2

    _10000, _10001 = _1000.children
    assert _10000.device == D["switch_2"] and _10000.port_index == 1
    assert len(_10000.children) == 1
    _100000 = _10000.children[0]
    assert _100000.device == D["switch_2"] and _100000.port_index == 0
    assert len(_100000.children) == 1

    _1000000 = _100000.children[0]
    assert _1000000.device == D["bus_0"] and _1000000.port_index == 0
    assert len(_1000000.children) == 2

    _10000000, _10000001 = _1000000.children

    assert _10000000.device == D["switch_0"] and _10000000.port_index == 1
    assert not _10000000.children

    assert _10000001.device == D["load_0"] and _10000001.port_index == 0
    assert not _10000001.children

    assert _10001.device == D["load_1"] and _10001.port_index == 0
    assert not _10001.children


def test_gen_forest_9(graph_fixture: AbstractPowerSupplySystemGraph):
    graph = graph_fixture

    D = graph.devices

    cast(Switch, D["switch_0"]).turn_on()
    cast(Switch, D["switch_1"]).turn_off()

    forest = graph.gen_forest()
    assert len(forest) == 2

    tree_0, tree_1 = forest
    assert len(tree_0.nodes) == 10
    for name in (
        "power_supply_0.0",
        "switch_0.0",
        "switch_0.1",
        "bus_0.0",
        "load_0.0",
        "switch_2.0",
        "switch_2.1",
        "bus_1.0",
        "switch_1.1",
        "load_1.0",
    ):
        assert name in tree_0.nodes
    assert len(tree_1.nodes) == 2
    for name in (
        "power_supply_1.0",
        "switch_1.0",
    ):
        assert name in tree_1.nodes

    _0, _1 = (t.root for t in forest)

    assert _1.device == D["power_supply_1"] and _1.port_index == 0
    assert len(_1.children) == 1

    _00 = _0.children[0]
    assert _00.device == D["switch_0"] and _00.port_index == 0
    assert len(_00.children) == 1

    _000 = _00.children[0]
    assert _000.device == D["switch_0"] and _000.port_index == 1
    assert len(_000.children) == 1

    _0000 = _000.children[0]
    assert _0000.device == D["bus_0"] and _0000.port_index == 0
    assert len(_0000.children) == 2

    _00000, _00001 = _0000.children

    assert _00000.device == D["switch_2"] and _00000.port_index == 0
    assert len(_00000.children) == 1

    _000000 = _00000.children[0]
    assert _000000.device == D["switch_2"] and _000000.port_index == 1
    assert len(_000000.children) == 1

    _0000000 = _000000.children[0]
    assert _0000000.device == D["bus_1"] and _0000000.port_index == 0
    assert len(_0000000.children) == 2

    _00000000, _00000001 = _0000000.children
    assert _00000000.device == D["switch_1"] and _00000000.port_index == 1
    assert not _00000000.children

    assert _00000001.device == D["load_1"] and _00000001.port_index == 0
    assert not _00000001.children

    assert _00001.device == D["load_0"] and _00001.port_index == 0
    assert not _00001.children


def test_gen_forest_10():
    graph = AbstractPowerSupplySystemGraph()
    graph.add_device(PowerSupply("power_supply"))
    graph.add_device(DcDc("dc_dc"))
    graph.add_edge(first=("power_supply", 0), second=("dc_dc", 0))
    graph.add_device(Switch("switch"))
    graph.add_edge(first=("dc_dc", 1), second=("switch", 0))
    graph.add_device(Load("load"))
    graph.add_edge(first=("switch", 1), second=("load", 0))

    forest = graph.gen_forest()

    assert len(forest) == 1
    tree = forest[0]
    assert len(tree.nodes) == 6

    for name in (
        "power_supply.0",
        "dc_dc.0",
        "dc_dc.1",
        "switch.0",
        "switch.1",
        "load.0",
    ):
        assert name in tree.nodes

    D = graph.devices
    _0 = tree.root
    assert _0.device == D["power_supply"] and _0.port_index == 0
    assert len(_0.children) == 1

    _00 = _0.children[0]
    assert _00.device == D["dc_dc"] and _00.port_index == 0
    assert len(_00.children) == 1

    _000 = _00.children[0]
    assert _000.device == D["dc_dc"] and _000.port_index == 1
    assert len(_000.children) == 1

    _0000 = _000.children[0]

    assert _0000.device == D["switch"] and _0000.port_index == 0
    assert len(_0000.children) == 1

    _00000 = _0000.children[0]
    assert _00000.device == D["switch"] and _00000.port_index == 1
    assert len(_00000.children) == 1

    _000000 = _00000.children[0]
    assert _000000.device == D["load"] and _000000.port_index == 0
    assert not _000000.children


def test_gen_forest_01():
    graph = AbstractPowerSupplySystemGraph()
    graph.add_device(PowerSupply("power_supply"))

    graph.add_device(Bus("bus_0"))
    graph.add_device(Bus("bus_1"))

    graph.add_edge(first=("power_supply", 0), second=("bus_0", 0))
    graph.add_edge(first=("power_supply", 0), second=("bus_1", 0))
    graph.add_edge(first=("bus_0", 0), second=("bus_1", 0))

    with pytest.raises(ChargePowerSupply):
        graph.gen_forest()


def test_find_passages_1(graph_fixture: AbstractPowerSupplySystemGraph):
    graph = graph_fixture

    truth_table = {"switch_0": True, "switch_1": True, "switch_2": False}
    passages = graph.find_passages((("load_0", 0), ("load_1", 0)), truth_table)
    assert len(passages) == 2
    assert len(passages["load_0.0"]) == 1
    assert len(passages["load_1.0"]) == 1
    for a, b in zip(
        (
            ("power_supply_0", 0),
            ("switch_0", 0),
            ("switch_0", 1),
            ("bus_0", 0),
            ("load_0", 0),
        ),
        passages["load_0.0"][0],
    ):
        assert a[0] == b.device_name and a[1] == b.index

    for a, b in zip(
        (
            ("power_supply_1", 0),
            ("switch_1", 0),
            ("switch_1", 1),
            ("bus_1", 0),
            ("load_1", 0),
        ),
        passages["load_1.0"][0],
    ):
        assert a[0] == b.device_name and a[1] == b.index


def test_find_passages_2(graph_fixture: AbstractPowerSupplySystemGraph):
    graph = graph_fixture

    D = graph.devices

    cast(Switch, D["switch_0"]).turn_on()
    cast(Switch, D["switch_1"]).turn_off()
    cast(Switch, D["switch_2"]).turn_on()

    truth_table = {
        "switch_0": True,
        "switch_1": False,
        "switch_2": True,
    }

    passages = graph.find_passages((("load_0", 0), ("load_1", 0)), truth_table)
    assert len(passages) == 2
    assert len(passages["load_0.0"]) == 1
    assert len(passages["load_1.0"]) == 1
    for a, b in zip(
        (
            ("power_supply_0", 0),
            ("switch_0", 0),
            ("switch_0", 1),
            ("bus_0", 0),
            ("load_0", 0),
        ),
        passages["load_0.0"][0],
    ):
        assert a[0] == b.device_name and a[1] == b.index

    for a, b in zip(
        (
            ("power_supply_0", 0),
            ("switch_0", 0),
            ("switch_0", 1),
            ("bus_0", 0),
            ("switch_2", 0),
            ("switch_2", 1),
            ("bus_1", 0),
            ("load_1", 0),
        ),
        passages["load_1.0"][0],
    ):
        assert a[0] == b.device_name and a[1] == b.index


def test_find_passages_3(graph_fixture: AbstractPowerSupplySystemGraph):
    graph = graph_fixture

    truth_table = {"switch_0": False, "switch_1": True, "switch_2": True}

    passages = graph.find_passages((("load_0", 0), ("load_1", 0)), truth_table)
    assert len(passages) == 2
    assert len(passages["load_0.0"]) == 1
    assert len(passages["load_1.0"]) == 1
    for a, b in zip(
        (
            ("power_supply_1", 0),
            ("switch_1", 0),
            ("switch_1", 1),
            ("bus_1", 0),
            ("switch_2", 1),
            ("switch_2", 0),
            ("bus_0", 0),
            ("load_0", 0),
        ),
        passages["load_0.0"][0],
    ):
        assert a[0] == b.device_name and a[1] == b.index

    for a, b in zip(
        (
            ("power_supply_1", 0),
            ("switch_1", 0),
            ("switch_1", 1),
            ("bus_1", 0),
            ("load_1", 0),
        ),
        passages["load_1.0"][0],
    ):
        assert a[0] == b.device_name and a[1] == b.index


def test_find_passages_4(graph_fixture: AbstractPowerSupplySystemGraph):
    graph = graph_fixture

    truth_table = {"switch_0": True, "switch_1": False, "switch_2": False}

    passages = graph.find_passages((("load_0", 0), ("load_1", 0)), truth_table)
    assert len(passages) == 1
    assert len(passages["load_0.0"]) == 1
    assert "load_1.0" not in passages
    for a, b in zip(
        (
            ("power_supply_0", 0),
            ("switch_0", 0),
            ("switch_0", 1),
            ("bus_0", 0),
            ("load_0", 0),
        ),
        passages["load_0.0"][0],
    ):
        assert a[0] == b.device_name and a[1] == b.index


def test_find_passages_5():
    g = AbstractPowerSupplySystemGraph()
    g.add_device(PowerSupply("power_supply_0"))
    g.add_device(PowerSupply("power_supply_1"))

    g.add_device(Switch("switch_0")).add_edge(("power_supply_0", 0), ("switch_0", 0))
    g.add_device(Switch("switch_1")).add_edge(("power_supply_1", 0), ("switch_1", 0))

    g.add_device(Bus("bus_0")).add_edge(("switch_0", 1), ("bus_0", 0))
    g.add_device(Bus("bus_1")).add_edge(("switch_1", 1), ("bus_1", 0))

    g.add_device(Diode("diode_0")).add_edge(("bus_0", 0), ("diode_0", 0))
    g.add_device(Diode("diode_1")).add_edge(("bus_1", 0), ("diode_1", 0))

    g.add_device(Load("load"))
    g.add_edge(("diode_0", 1), ("load", 0))
    g.add_edge(("diode_1", 1), ("load", 0))

    passages = g.find_passages((("load", 0),), {"switch_0": True, "switch_1": True})
    assert len(passages) == 1
    assert len(passages["load.0"]) == 2

    for a, b in zip(
        (
            "power_supply_0.0",
            "switch_0.0",
            "switch_0.1",
            "bus_0.0",
            "diode_0.0",
            "diode_0.1",
            "load.0",
        ),
        passages["load.0"][0],
    ):
        assert a == b.id

    for a, b in zip(
        (
            "power_supply_1.0",
            "switch_1.0",
            "switch_1.1",
            "bus_1.0",
            "diode_1.0",
            "diode_1.1",
            "load.0",
        ),
        passages["load.0"][1],
    ):
        assert a == b.id

    passages = g.find_passages((("load", 0),), {"switch_0": False, "switch_1": True})
    assert len(passages) == 1
    assert len(passages["load.0"]) == 1

    for a, b in zip(
        (
            "power_supply_1.0",
            "switch_1.0",
            "switch_1.1",
            "bus_1.0",
            "diode_1.0",
            "diode_1.1",
            "load.0",
        ),
        passages["load.0"][0],
    ):
        assert a == b.id
