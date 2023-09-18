import pprint

from apssdag.builder import AbstractPowerSupplySystemDagBuilder
from apssdag.devices.bus import Bus
from apssdag.devices.dc_dc_converter import DcDc
from apssdag.devices.load import Load
from apssdag.devices.power_supply import PowerSupply
from apssdag.devices.switch import Switch


def main():
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

    pprint.pprint(dag.nodes)


if __name__ == "__main__":
    main()
