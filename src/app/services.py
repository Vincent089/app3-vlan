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
import itertools
import uuid
from typing import List, Optional
from ipaddress import IPv4Network
from app.models import Core, Vlan, VlanRestrictionRange
from app.uow import UnitOfWork
from common.execptions import DomainError, NotFoundError, AlreadyExistsError

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

    def update_core(self, core_id: int, name: Optional[str] = None, group: Optional[str] = None) -> Optional[Core]:
        with UnitOfWork() as uow:
            core = uow.cores.get(core_id)

            if not core:
                raise NotFoundError(f"Core with id {core_id} not found")

            if name is not None:
                core.name = name
            if group is not None:
                core.group = group

            return core

    def delete_core(self, core_id: int) -> bool:
        with UnitOfWork() as uow:
            core = uow.cores.get(core_id)

            if not core:
                raise NotFoundError(f"Core with id {core_id} not found")

            # Check for attached VLANs
            vlans = uow.vlans.list(core)
            if vlans:
                raise DomainError(f"Core {core.name} has attached VLANs and cannot be deleted.")

            uow.cores.delete(core)
            return True


class VlanService:

    def create_vlan(self, subnet: IPv4Network, core_id: int, gcode: str, purpose: str, number: Optional[int] = None,
                    name: Optional[str] = None, description: Optional[str] = None) -> Vlan:
        with UnitOfWork() as uow:
            core = uow.cores.get(core_id)

            if not core:
                raise NotFoundError(f"Core with id {core_id} not found")

            if number:
                # Check if vlan number already exists in the same core
                if uow.vlans.get_by_number(core, number):
                    raise AlreadyExistsError(f"Vlan {number} already exists in core {core.name}")

                # Check if vlan number already exists in the same core group
                if core.group:
                    existing_vlan = uow.vlans.get_by_number_and_core_group(number, core.group)

                    if existing_vlan:
                        raise AlreadyExistsError(
                                f"Vlan {number} already exists in core {existing_vlan.core.name} (Group: {core.group})"
                        )
            else:
                # Set number to next available in core group
                vlans_in_group = uow.vlans.list_by_core_group(core.group)
                restricted_vlan_ranges = uow.ranges.list(core)

                used_vlan_numbers = [v.number for v in vlans_in_group]
                restricted_numbers = list(itertools.chain(*[r.range_array for r in restricted_vlan_ranges]))
                used_numbers = set(used_vlan_numbers + restricted_numbers)

                number = 2

                while number in used_numbers:
                    number += 1

            vlan = Vlan(number=number, subnet=subnet, core=core, gcode=gcode, purpose=purpose,
                        name=name, description=description)
            uow.vlans.add(vlan)
            return vlan

    def get_vlan(self, vlan_id: uuid.UUID) -> Optional[Vlan]:
        with UnitOfWork() as uow:
            return uow.vlans.get(vlan_id)

    def get_vlan_by_number(self, core_id: int, vlan_number: int) -> Optional[Vlan]:
        with UnitOfWork() as uow:
            core = uow.cores.get(core_id)

            if not core:
                raise NotFoundError(f"Core with id {core_id} not found")

            return uow.vlans.get_by_number(core, vlan_number)

    def list_vlans(self, core_id: Optional[int]) -> List[Vlan]:
        with UnitOfWork() as uow:
            core = None
            if core_id:
                core = uow.cores.get(core_id)
            return uow.vlans.list(core)

    def update_vlan(self, name: Optional[str] = None, description: Optional[str] = None, gcode: Optional[str] = None,
                    purpose: Optional[str] = None, core_id: Optional[int] = None, number: Optional[int] = None,
                    vlan_id: Optional[uuid.UUID] = None) -> Optional[Vlan]:
        with UnitOfWork() as uow:

            if core_id and number:
                core = uow.cores.get(core_id)
                vlan = uow.vlans.get_by_number(core, number)

            if vlan_id:
                vlan = uow.vlans.get(vlan_id)

            if not vlan:
                raise NotFoundError(f"Vlan not found")

            if name is not None:
                vlan.name = name
            if description is not None:
                vlan.description = description
            if gcode is not None:
                vlan.gcode = gcode
            if purpose is not None:
                vlan.purpose = purpose

            return vlan

    def delete_vlan(self, core_id: Optional[int] = None, number: Optional[int] = None,
                    vlan_id: Optional[uuid.UUID] = None):
        with UnitOfWork() as uow:
            if core_id and number:
                core = uow.cores.get(core_id)
                vlan = uow.vlans.get_by_number(core, number)

            if vlan_id:
                vlan = uow.vlans.get(vlan_id)

            if not vlan:
                raise NotFoundError(f"Vlan not found")

            uow.vlans.delete(vlan)
            return True


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
