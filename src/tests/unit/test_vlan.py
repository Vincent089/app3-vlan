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
from ipaddress import IPv4Network
from app.models import Core, Vlan


@pytest.fixture
def core():
    return Core(datacenter="DDC", name="Core01", size=4096)


@pytest.fixture
def subnet():
    return IPv4Network("10.0.0.0/24")


def test_vlan_default_name(core, subnet):
    vlan = Vlan(number=10, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')
    assert vlan.name == f"{subnet}_G123_TEST_VLAN"


def test_vlan_custom_name_is_uppercase(core, subnet):
    vlan = Vlan(number=10, subnet=subnet, core=core, gcode="G123", name="my-vlan", purpose='test-vlan')
    assert vlan.name == "MY_VLAN"


def test_vlan_str_representation(core, subnet):
    vlan = Vlan(number=10, subnet=subnet, core=core, gcode="G123", name="Production", purpose='test-vlan')
    assert str(vlan) == "PRODUCTION"


def test_vlan_repr(core, subnet):
    vlan = Vlan(number=10, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')
    assert repr(vlan) == "<Vlan CORE01 10>"


def test_vlan_number_too_low_raises_error(core, subnet):
    with pytest.raises(ValueError):
        Vlan(number=1, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')


def test_vlan_number_exceeds_core_size_raises_error(core, subnet):
    with pytest.raises(ValueError):
        Vlan(number=5000, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')


def test_vlan_equality(core, subnet):
    vlan1 = Vlan(number=10, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')
    vlan2 = Vlan(number=10, subnet=subnet, core=core, gcode="G456", purpose='test-vlan')
    vlan3 = Vlan(number=20, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')
    assert vlan1 == vlan2
    assert vlan1 != vlan3

def test_vlan_sorting(core, subnet):
    vlan1 = Vlan(number=10, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')
    vlan2 = Vlan(number=30, subnet=subnet, core=core, gcode="G456", purpose='test-vlan')
    vlan3 = Vlan(number=20, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')

    vlans = [vlan1, vlan2, vlan3]
    sorted_vlans = sorted(vlans)

    assert sorted_vlans == [vlan1, vlan3, vlan2]


def test_vlan_max_select(core, subnet):
    vlan1 = Vlan(number=10, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')
    vlan2 = Vlan(number=30, subnet=subnet, core=core, gcode="G456", purpose='test-vlan')
    vlan3 = Vlan(number=20, subnet=subnet, core=core, gcode="G123", purpose='test-vlan')

    vlans = [vlan1, vlan2, vlan3]
    max_vlan = max(vlans)

    assert max_vlan == vlan2
