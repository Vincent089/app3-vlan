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

from typing import List
from unittest.mock import MagicMock
from app.models import Core, VlanRestrictionRange
from app.services import VlanRestrictionService
from common.execptions import NotFoundError


@pytest.fixture
def core():
    return Core(datacenter="DDC", name="Core01", size=4096)


@pytest.fixture
def mock_uow(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('app.services.UnitOfWork', lambda: mock)
    mock.__enter__.return_value = mock
    return mock


def test_create_vlan_restriction(mock_uow, core):
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.get.return_value = core

    service = VlanRestrictionService()
    vlan_range = service.create_vlan_restriction(core_id=1, description="Test Range", start=100, end=200)

    assert vlan_range.core == core
    assert vlan_range.description == "Test Range"
    assert vlan_range.start == 100
    assert vlan_range.end == 200


def test_create_vlan_restriction_core_not_found(mock_uow):
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.get.return_value = None

    service = VlanRestrictionService()

    with pytest.raises(NotFoundError, match="Core with id 1 not found"):
        service.create_vlan_restriction(core_id=1, description="Test Range", start=100, end=200)


def test_get_vlan_restriction(mock_uow, core):
    expected_range = VlanRestrictionRange(core=core, description="Test Range", start=100, end=200)

    mock_uow.__enter__.return_value = mock_uow
    mock_uow.ranges.get.return_value = expected_range

    service = VlanRestrictionService()
    vlan_range = service.get_vlan_restriction(range_id=1)

    assert vlan_range == expected_range


def test_list_vlan_restrictions(mock_uow, core):
    expected_ranges = [
        VlanRestrictionRange(core=core, description="Test Range 1", start=100, end=200),
        VlanRestrictionRange(core=core, description="Test Range 2", start=300, end=400)
    ]

    mock_uow.__enter__.return_value = mock_uow
    mock_uow.cores.get.return_value = core
    mock_uow.ranges.list.return_value = MagicMock(spec=List[VlanRestrictionRange],
                                                  __iter__=lambda x: iter(expected_ranges))

    service = VlanRestrictionService()
    vlan_ranges = service.list_vlan_restrictions(core_id=1)

    assert list(vlan_ranges) == expected_ranges

def test_update_vlan_restriction(mock_uow, core):
    existing_range = VlanRestrictionRange(core=core, description="Old Description", start=100, end=200)

    mock_uow.__enter__.return_value = mock_uow
    mock_uow.ranges.get.return_value = existing_range

    service = VlanRestrictionService()
    updated_range = service.update_vlan_restriction(range_id=1, description="New Description", end=250)

    assert updated_range.description == "New Description"
    assert updated_range.start == 100
    assert updated_range.end == 250


def test_update_vlan_restriction_not_found(mock_uow):
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.ranges.get.return_value = None

    service = VlanRestrictionService()

    with pytest.raises(NotFoundError, match="VlanRestrictionRange with id 1 not found"):
        service.update_vlan_restriction(range_id=1, description="New Description")


def test_delete_vlan_restriction(mock_uow, core):
    existing_range = VlanRestrictionRange(core=core, description="Test Range", start=100, end=200)

    mock_uow.__enter__.return_value = mock_uow
    mock_uow.ranges.get.return_value = existing_range

    service = VlanRestrictionService()

    result = service.delete_vlan_restriction(range_id=1)

    assert result is True


def test_delete_vlan_restriction_not_found(mock_uow):
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.ranges.get.return_value = None

    service = VlanRestrictionService()

    with pytest.raises(NotFoundError, match="VlanRestrictionRange with id 1 not found"):
        service.delete_vlan_restriction(range_id=1)
