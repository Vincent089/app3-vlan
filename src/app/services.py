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
from app.models import Datacenter, Core, Vlan, VlanRestrictionRange
from app.schemas import DatacenterSchema
from app.uow import UnitOfWork


class DatacenterService:
    datacenter_schema = DatacenterSchema()

    def create_datacenter(self, name: str) -> Datacenter:
        with UnitOfWork() as uow:
            datacenter = Datacenter(name=name)
            uow.datacenters.add(datacenter)

            return self.datacenter_schema.dump(
                datacenter
            )

    def get_datacenter(self, datacenter_id: int) -> Optional[Datacenter]:
        with UnitOfWork() as uow:
            return self.datacenter_schema.dump(
                uow.datacenters.get(datacenter_id)
            )

    def list_datacenters(self) -> List[Datacenter]:
        with UnitOfWork() as uow:
            return self.datacenter_schema.dump(
                uow.datacenters.list(),
                many=True
            )

    def update_datacenter(self, datacenter_id: int, name: str) -> Optional[Datacenter]:
        with UnitOfWork() as uow:
            datacenter = uow.datacenters.get(datacenter_id)

            if datacenter:
                datacenter.name = name

            return self.datacenter_schema.dump(
                datacenter
            )

    def delete_datacenter(self, datacenter_id: int) -> bool:
        with UnitOfWork() as uow:
            datacenter = uow.datacenters.get(datacenter_id)

            if datacenter:
                uow.datacenters.delete(datacenter)
                return True

            return False


class CoreService:

    def create_core(self, datacenter_id: int, name: str, size: int = 4096, group: Optional[str] = None) -> Core:
        with UnitOfWork() as uow:
            core = Core(datacenter_id=datacenter_id, name=name, size=size, group=group)
            uow.cores.add(core)
            return core

    def get_core(self, core_id: int) -> Optional[Core]:
        with UnitOfWork() as uow:
            return uow.cores.get(core_id)

    def list_cores(self, datacenter_id: Optional[int] = None) -> List[Core]:
        with UnitOfWork() as uow:
            return uow.cores.list(datacenter_id)

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

    def delete_core(self, core_id: int) -> bool:
        with UnitOfWork() as uow:
            core = uow.cores.get(core_id)
            if core:
                uow.cores.delete(core)
                return True
            return False


class VlanService:

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
