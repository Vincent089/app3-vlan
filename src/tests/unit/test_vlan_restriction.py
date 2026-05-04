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
from app.models import Core, VlanRestrictionRange


@pytest.fixture
def core():
    return Core(datacenter="DDC", name="Core01", size=4096)


def test_vlan_restriction_range_initialization(core):
    vlan_range = VlanRestrictionRange(core=core, description='test range', start=10, end=20)
    assert vlan_range.start == 10
    assert vlan_range.end == 20


def test_vlan_restriction_range_validation_error(core):
    with pytest.raises(ValueError):
        VlanRestrictionRange(core=core, description='test range', start=100, end=50)


def test_vlan_restriction_range_out_of_bounds(core):
    with pytest.raises(ValueError):
        VlanRestrictionRange(core=core, description='test range', start=0, end=10)

    with pytest.raises(ValueError):
        VlanRestrictionRange(core=core, description='test range', start=10, end=4097)


def test_vlan_restriction_range_contains(core):
    vlan_range = VlanRestrictionRange(core=core, description='test range', start=100, end=200)
    assert 100 in vlan_range
    assert 150 in vlan_range
    assert 200 in vlan_range
    assert 99 not in vlan_range
    assert 201 not in vlan_range


def test_vlan_restriction_range_repr(core):
    vlan_range = VlanRestrictionRange(core=core, description='test range', start=10, end=20)
    assert repr(vlan_range) == "<VlanRestrictionRange CORE01 (10-20)>"


def test_vlan_restriction_range_array(core):
    vlan_range = VlanRestrictionRange(core=core, description='test range', start=10, end=20)
    expected_range = range(10, 21)
    assert vlan_range.range_array == list(expected_range)
