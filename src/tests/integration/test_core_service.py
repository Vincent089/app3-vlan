#   -----------------------------------------------------------------------------
#  Copyright (c) 2026. Vincent Corriveau (vincent.corriveau89@gmail.com)
#
#  Licensed under the MIT License. You. may obtain a copy of the License at
#  https://opensource.org/licenses/MIT
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  -----------------------------------------------------------------------------
import pytest
from typing import List
from unittest.mock import MagicMock
from app.services import CoreService, VlanService
from ipaddress import IPv4Network
from app.models import Core, Vlan
from common.execptions import DomainError, NotFoundError


@pytest.fixture
def mock_uow(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('app.services.UnitOfWork', lambda: mock)
    mock.__enter__.return_value = mock
    return mock


def test_creaaate_core(mock_uow):
    mock_uow.__enter__.return_value = mock_uow

    service = CoreService()

    core = service.create_core(datacenter="DDC1", name="CORE01", size=1024, group="GROUP1")

    assert core.datacenter == "DDC1"
    assert core.name == "CORE01"
    assert core.size == 1024
    assert core.group == "GROUP1"


def test_get_core(mock_uow):
    core = Core(datacenter="DDC", name="Core01", size=4096, group="PROD")

    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.get.return_value = core

    service = CoreService()

    retrieved_core = service.get_core(1)
    assert retrieved_core.name == "CORE01"


def test_list_cores(mock_uow):
    cores = [
        Core(datacenter="DDC", name="Core01", size=4096, group="PROD"),
        Core(datacenter="DDC", name="Core02", size=4096, group="PROD"),
        Core(datacenter="MDC", name="Core02", size=4096)
    ]

    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.list.return_value = MagicMock(spec=List[Core], __iter__=lambda x: iter(cores))

    service = CoreService()

    cores_ddc1 = service.list_cores(datacenter="DDC")
    assert { c.name for c in cores_ddc1 } == { "CORE01", "CORE02" }

    all_cores = service.list_cores()
    assert cores == list(all_cores)


def test_update_core(mock_uow):
    core = Core(datacenter="DDC", name="Core01", size=4096, group="PROD")

    mock_uow.__enter__.return_value = mock_uow

    service = CoreService()

    updated_core = service.update_core(1, name="NEWCORE", group="GROUP2")

    assert updated_core.name == "NEWCORE"
    assert updated_core.group == "GROUP2"

    retrieved_core = service.get_core(1)
    assert retrieved_core.name == "NEWCORE"
    assert retrieved_core.group == "GROUP2"


def test_update_core_not_found(mock_uow):
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.get.return_value = None

    service = CoreService()

    with pytest.raises(NotFoundError, match="Core with id 999 not found"):
        service.update_core(999, name="NONEXISTENT")


def test_delete_core(mock_uow):
    core = Core(datacenter="DDC", name="Core01", size=4096, group="PROD")

    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.get.return_value = core
    mock_uow.vlans.list.return_value = None

    service = CoreService()

    assert service.delete_core(core.id) is True


def test_delete_core_with_vlans_attached(mock_uow):
    core = Core(datacenter="DDC", name="Core01", size=4096, group="PROD")
    vlans = [
        Vlan(number=2, subnet=IPv4Network("192.168.1.0/24"), core=core, gcode="G123", purpose='test-vlan'),
        Vlan(number=4, subnet=IPv4Network("10.0.0.0/24"), core=core, gcode="G456", purpose='test-vlan')
    ]

    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.get.return_value = core
    mock_uow.ranges.list.return_value = MagicMock(spec=List[Vlan], __iter__=lambda x: iter(vlans))

    service = CoreService()

    with pytest.raises(DomainError, match=f"Core {core.name} has attached VLANs and cannot be deleted."):
        service.delete_core(core.id)


def test_delete_core_not_found(mock_uow):
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.get.return_value = None

    service = CoreService()

    with pytest.raises(NotFoundError, match="Core with id 999 not found"):
        service.delete_core(999)
