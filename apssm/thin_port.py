from typing import NamedTuple

from apssm import gen_port_id


class ThinPort(NamedTuple):
    device_name: str
    index: int

    @property
    def id(self):
        return gen_port_id.gen_port_id(self.device_name, self.index)
