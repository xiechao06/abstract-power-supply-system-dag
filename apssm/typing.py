from apssm.devices.bus import Bus
from apssm.devices.dc_dc import DcDc
from apssm.devices.diode import Diode
from apssm.devices.load import Load
from apssm.devices.power_supply import PowerSupply
from apssm.devices.switch import Switch
from apssm.thin_port import ThinPort

DeviceType = PowerSupply | Switch | DcDc | Bus | Load | Diode
