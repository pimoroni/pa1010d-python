import pytest
import mock
import sys


@pytest.fixture(scope='function', autouse=False)
def smbus():
    smbus = mock.MagicMock()
    sys.modules["smbus"] = smbus
    yield smbus
    del sys.modules["smbus"]
