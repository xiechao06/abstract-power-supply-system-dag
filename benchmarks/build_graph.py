from apssm.devices.bus import Bus
from apssm.devices.dc_dc import DcDc
from apssm.devices.load import Load
from apssm.devices.power_supply import PowerSupply
from apssm.devices.switch import Switch
from apssm.graph import AbstractPowerSupplySystemGraph


def build_graph(level1: int, level2: int):
    graph = AbstractPowerSupplySystemGraph()

    graph.add_device(PowerSupply("power_supply_0"))
    graph.add_device(PowerSupply("power_supply_1"))

    graph.add_device(DcDc("dc_dc_0"))
    graph.add_edge(first=("power_supply_0", 0), second=("dc_dc_0", 0))
    graph.add_device(DcDc("dc_dc_1"))
    graph.add_edge(first=("power_supply_1", 0), second=("dc_dc_1", 0))

    graph.add_device(Switch("switch_0"))
    graph.add_edge(first=("dc_dc_0", 1), second=("switch_0", 0))
    graph.add_device(Switch("switch_1"))
    graph.add_edge(first=("dc_dc_1", 1), second=("switch_1", 0))

    for i in range(level1):
        graph.add_device(Bus(f"bus_0_{i}"))
        graph.add_edge(first=("switch_0", 1), second=(f"bus_0_{i}", 0))
        graph.add_device(Bus(f"bus_1_{i}"))
        graph.add_edge(first=("switch_1", 1), second=(f"bus_1_{i}", 0))

        for j in range(level2):
            graph.add_device(Switch(f"switch_0_{i}_{j}"))
            graph.add_edge(first=(f"bus_0_{i}", 0), second=(f"switch_0_{i}_{j}", 0))
            graph.add_device(Load(f"load_0_{i}_{j}"))
            graph.add_edge(
                first=(f"switch_0_{i}_{j}", 1), second=(f"load_0_{i}_{j}", 0)
            )

            graph.add_device(Switch(f"switch_1_{i}_{j}"))
            graph.add_edge(first=(f"bus_1_{i}", 0), second=(f"switch_1_{i}_{j}", 0))
            graph.add_device(Load(f"load_1_{i}_{j}"))
            graph.add_edge(
                first=(f"switch_1_{i}_{j}", 1), second=(f"load_1_{i}_{j}", 0)
            )

    return graph
