import sys

import mock
import pytest


class SMBus:
    def __init__(self, bus):
        self.data = "$PMTK011,MTKGPS*08\r\n".encode("ascii")
        self.ptr = 0

    def read_byte_data(self, address, register):
        if register == 0x00:
            result = self.data[self.ptr]
            self.ptr += 1
            self.ptr %= len(self.data)
            return result
        else:
            return 0

    def write_byte(self, address, data):
        pass


@pytest.fixture(scope='function', autouse=False)
def smbus():
    smbus = mock.MagicMock()
    smbus.SMBus = SMBus
    sys.modules["smbus"] = smbus
    yield smbus
    del sys.modules["smbus"]
