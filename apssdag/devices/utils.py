from apssdag.devices.base_device import BaseDeviceData
from apssdag.devices.bus import Bus
from apssdag.devices.dc_dc_converter import DcDc
from apssdag.devices.load import Load
from apssdag.devices.power_supply import PowerSupply
from apssdag.devices.switch import Switch, SwitchData


def get_exact_device_type(data: BaseDeviceData):
    if isinstance(data, PowerSupply):
        return PowerSupply
    elif isinstance(data, SwitchData):
        return Switch
    elif isinstance(data, DcDc):
        return DcDc
    elif isinstance(data, Bus):
        return Bus
    else:
        return Load
