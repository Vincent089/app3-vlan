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

from typing import List, Optional
from ipaddress import IPv4Network
from app.models import Core, Vlan, VlanRestrictionRange
from app.uow import UnitOfWork


class CoreService:

    def create_core(self, datacenter: str, name: str, size: int = 4096, group: Optional[str] = None) -> Core:
        with UnitOfWork() as uow:
            core = Core(datacenter=datacenter, name=name, size=size, group=group)
            uow.cores.add(core)
            return core

    def get_core(self, core_id: int) -> Optional[Core]:
        with UnitOfWork() as uow:
            return uow.cores.get(core_id)

    def list_cores(self, datacenter: Optional[str] = None) -> List[Core]:
        with UnitOfWork() as uow:
            return uow.cores.list(datacenter)

    def update_core(self, core_id: int, name: Optional[str] = None, size: Optional[int] = None,
                    group: Optional[str] = None) -> Optional[Core]:
        with UnitOfWork() as uow:
            core = uow.cores.get(core_id)
            if core:
                if name is not None:
                    core.name = name
                if size is not None:
                    core.size = size
                if group is not None:
                    core.group = group
            return core


class VlanService:

    def create_vlan(self, number: int, subnet: IPv4Network, core_id: int, gcode: str, purpose: str,
                    name: Optional[str] = None, description: Optional[str] = None) -> Vlan:
        with UnitOfWork() as uow:
            core = uow.cores.get(core_id)
            if not core:
                raise ValueError(f"Core with id {core_id} not found")

            # Check if vlan number already exists in the same core
            if uow.vlans.get_by_number(core, number):
                raise ValueError(f"Vlan {number} already exists in core {core.name}")

            # Check if vlan number already exists in the same core group
            if core.group:
                existing_vlan = uow.vlans.get_by_number_and_core_group(number, core.group)
                if existing_vlan:
                    raise ValueError(
                        f"Vlan {number} already exists in core {existing_vlan.core.name} (Group: {core.group})"
                    )

            vlan = Vlan(number=number, subnet=subnet, core=core, gcode=gcode, purpose=purpose,
                        name=name, description=description)
            uow.vlans.add(vlan)
            return vlan

    def get_vlan(self, vlan_id: int) -> Optional[Vlan]:
        with UnitOfWork() as uow:
            return uow.vlans.get(vlan_id)

    def list_vlans(self, core_id: Optional[int]) -> List[Vlan]:
        with UnitOfWork() as uow:
            core = None
            if core_id:
                core = uow.cores.get(core_id)
            return uow.vlans.list(core)


class VlanRestrictionService:

    def get_vlan_restriction_range(self, range_id: int) -> Optional[VlanRestrictionRange]:
        with UnitOfWork() as uow:
            return uow.ranges.get(range_id)

    def list_vlan_restriction_ranges(self, core_id: Optional[int]) -> List[VlanRestrictionRange]:
        with UnitOfWork() as uow:
            core = None
            if core_id:
                core = uow.cores.get(core_id)
            return uow.ranges.list(core)
