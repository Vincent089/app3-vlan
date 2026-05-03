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
from app.services import CoreService, VlanService
from app.uow import UnitOfWork
from ipaddress import IPv4Network


@pytest.fixture
def core_service():
    return CoreService()

@pytest.fixture
def vlan_service():
    return VlanService()

@pytest.fixture(autouse=True)
def setup_teardown_db():
    # Setup: Clear the database before each test
    with UnitOfWork() as uow:
        uow.vlans.delete_all()
        uow.cores.delete_all()
        uow.ranges.delete_all()
        uow.commit()
    yield
    # Teardown: Clear the database after each test
    with UnitOfWork() as uow:
        uow.vlans.delete_all()
        uow.cores.delete_all()
        uow.ranges.delete_all()
        uow.commit()

def test_create_core(core_service: CoreService):
    core = core_service.create_core(datacenter="DDC1", name="CORE01", size=1024, group="GROUP1")
    assert core.id is not None
    assert core.datacenter == "DDC1"
    assert core.name == "CORE01"
    assert core.size == 1024
    assert core.group == "GROUP1"

    retrieved_core = core_service.get_core(core.id)
    assert retrieved_core == core

def test_get_core(core_service: CoreService):
    core = core_service.create_core(datacenter="DDC1", name="CORE01")
    retrieved_core = core_service.get_core(core.id)
    assert retrieved_core.name == "CORE01"

def test_list_cores(core_service: CoreService):
    core_service.create_core(datacenter="DDC1", name="CORE01")
    core_service.create_core(datacenter="DDC1", name="CORE02")
    core_service.create_core(datacenter="DDC2", name="CORE03")

    cores_ddc1 = core_service.list_cores(datacenter="DDC1")
    assert len(cores_ddc1) == 2
    assert {c.name for c in cores_ddc1} == {"CORE01", "CORE02"}

    all_cores = core_service.list_cores()
    assert len(all_cores) == 3

def test_update_core(core_service: CoreService):
    core = core_service.create_core(datacenter="DDC1", name="CORE01", group="GROUP1")
    updated_core = core_service.update_core(core.id, name="NEWCORE", group="GROUP2")
    assert updated_core.name == "NEWCORE"
    assert updated_core.group == "GROUP2"

    retrieved_core = core_service.get_core(core.id)
    assert retrieved_core.name == "NEWCORE"
    assert retrieved_core.group == "GROUP2"

def test_update_core_not_found(core_service: CoreService):
    updated_core = core_service.update_core(999, name="NONEXISTENT")
    assert updated_core is None

def test_delete_core(core_service: CoreService):
    core = core_service.create_core(datacenter="DDC1", name="CORE01")
    assert core_service.get_core(core.id) is not None
    core_service.delete_core(core.id)
    assert core_service.get_core(core.id) is None

def test_delete_core_with_vlans_attached(core_service: CoreService, vlan_service: VlanService):
    core = core_service.create_core(datacenter="DDC1", name="CORE01")
    vlan_service.create_vlan(subnet=IPv4Network("192.168.1.0/24"), core_id=core.id, gcode="G1", purpose="P1", number=10)

    with pytest.raises(ValueError, match=f"Core {core.name} has attached VLANs and cannot be deleted."):
        core_service.delete_core(core.id)

    assert core_service.get_core(core.id) is not None

def test_delete_core_not_found(core_service: CoreService):
    core_service.delete_core(999) # Should not raise an error, just do nothing
    assert core_service.get_core(999) is None
