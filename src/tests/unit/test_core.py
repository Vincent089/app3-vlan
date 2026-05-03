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
from app.models import Core


def test_core_creation():
    core = Core(datacenter="DDC", name="Core01", size=1024, group="MGMT")
    assert core.name == "Core01"
    assert core.datacenter == "DDC"
    assert core.size == 1024
    assert core.group == "MGMT"


def test_core_default_size():
    core = Core(datacenter="DDC", name="Core01")
    assert core.size == 4096


def test_core_size_limit():
    with pytest.raises(ValueError, match="Core size must be between 1 and 4096"):
        Core(datacenter="DDC", name="Core01", size=5000)


def test_core_size_update_locked():
    core = Core(datacenter="DDC", name="Core01", size=1024)
    with pytest.raises(AttributeError, match="Cannot modify read-only attribute 'size'"):
        core.size = 8192


def test_core_name_always_uppercase():
    core = Core(datacenter="DDC", name="core01")
    assert core.name == "CORE01"
    core_mixed = Core(datacenter="DDC", name="Core-Test")
    assert core_mixed.name == "CORE-TEST"
