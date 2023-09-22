import pprint

from apssm.devices.bus import Bus
from apssm.devices.dc_dc import DcDc
from apssm.devices.load import Load
from apssm.devices.power_supply import PowerSupply
from apssm.devices.switch import Switch
from apssm.graph import AbstractPowerSupplySystemGraph


def main():
    graph = AbstractPowerSupplySystemGraph()

    graph.add_device(PowerSupply(name="power_supply_1"))

    graph.add_device(Switch(name="switch_1"))
    graph.add_edge(first=("power_supply_1", 0), second=("switch_1", 0))

    graph.add_device(DcDc(name="dc_dc_1"))
    graph.add_edge(first=("switch_1", 1), second=("dc_dc_1", 0))

    graph.add_device(Bus(name="bus_1"))
    graph.add_edge(first=("dc_dc_1", 1), second=("bus_1", 0))

    graph.add_device(Switch(name="switch_2"))
    graph.add_edge(first=("bus_1", 0), second=("switch_2", 0))

    graph.add_device(Load(name="load_1"))
    graph.add_edge(first=("switch_2", 1), second=("load_1", 0))

    forest = graph.gen_forest()

    for tree in forest:
        pprint.pprint(tree)


if __name__ == "__main__":
    main()
