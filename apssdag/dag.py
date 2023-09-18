from apssdag.connection import Connection
from apssdag.devices.bus import Bus
from apssdag.devices.dc_dc_converter import DcDc
from apssdag.devices.load import Load
from apssdag.devices.power_supply import PowerSupply
from apssdag.devices.switch import Switch
from apssdag.node import Node


class AbstractPowerSupplySystemDag:
    roots: list[Node[PowerSupply]]
    conns: dict[str, list[Connection]]
    nodes: dict[str, Node[PowerSupply | Switch | DcDc | Bus | Load]]

    def __init__(self):
        self.roots = []
        self.conns = {}
        self.nodes = {}
        self.nodes = {}
