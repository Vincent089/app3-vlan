#   -----------------------------------------------------------------------------
#  Copyright (c) 2026. Vincent Corriveau (vincent.corriveau89@gmail.com)
#
#  Licensed under the MIT License. You may obtain a copy of the License at
#  https://opensource.org/licenses/MIT
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  -----------------------------------------------------------------------------
import pytest
from unittest.mock import MagicMock
from ipaddress import IPv4Network
from app.models import Core, Vlan
from app.services import VlanService

@pytest.fixture
def core():
    return Core(datacenter="DDC", name="Core01", size=4096)

@pytest.fixture
def subnet():
    return IPv4Network("10.0.0.0/24")

@pytest.fixture
def mock_uow(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('app.services.UnitOfWork', lambda: mock)
    mock.__enter__.return_value = mock
    return mock

def test_vlan_uniqueness_same_core(mock_uow, core, subnet):
    mock_uow.__enter__.return_value = mock_uow

    mock_uow.cores.get.return_value = core
    mock_uow.vlans.get_by_number.return_value = MagicMock(spec=Vlan)

    service = VlanService()
    with pytest.raises(ValueError, match="already exists in core Core01"):
        service.create_vlan(number=10, subnet=subnet, core_id=1, gcode="G123", purpose='test')


def test_vlan_uniqueness_different_core_same_group(mock_uow, subnet):
    core1 = Core(datacenter="DDC", name="Core01", size=4096, group="PROD")
    core2 = Core(datacenter="DDC", name="Core02", size=4096, group="PROD")

    mock_uow.__enter__.return_value = mock_uow

    mock_uow.cores.get.return_value = core2
    mock_uow.vlans.get_by_number.return_value = None

    existing_vlan = MagicMock(spec=Vlan)
    existing_vlan.core = core1
    mock_uow.vlans.get_by_number_and_core_group.return_value = existing_vlan

    service = VlanService()
    with pytest.raises(ValueError, match="already exists in core Core01"):
        service.create_vlan(number=10, subnet=subnet, core_id=2, gcode="G123", purpose='test')
