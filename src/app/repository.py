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
from sqlalchemy.orm import Session
from app.models import Core, Vlan, VlanRestrictionRange


class CoreRepository:

    def __init__(self, session: Session):
        self.session = session

    def add(self, core: Core):
        self.session.add(core)

    def get(self, core_id: int) -> Optional[Core]:
        return self.session.query(Core).filter_by(id=core_id).first()

    def get_by_name(self, name: str) -> Optional[Core]:
        return self.session.query(Core).filter_by(name=name).first()

    def list(self, datacenter: Optional[str] = None) -> list[type[Core]]:
        query = self.session.query(Core)
        if datacenter:
            query = query.filter_by(datacenter=datacenter)
        return query.all()

    def delete(self, core: Core):
        self.session.delete(core)


class VlanRepository:

    def __init__(self, session: Session):
        self.session = session

    def add(self, vlan: Vlan):
        self.session.add(vlan)

    def get(self, vlan_id: int) -> Optional[Vlan]:
        return self.session.query(Vlan).filter_by(id=vlan_id).first()

    def get_by_number(self, core: Core, number: int) -> Optional[Vlan]:
        return self.session.query(Vlan).filter_by(core=core, _number=number).first()

    def list(self, core: Optional[Core] = None) -> list[type[Vlan]]:
        query = self.session.query(Vlan)
        if core:
            query = query.filter_by(core=core)
        return query.all()

    def delete(self, vlan: Vlan):
        self.session.delete(vlan)


class VlanRestrictionRangeRepository:

    def __init__(self, session: Session):
        self.session = session

    def add(self, range: VlanRestrictionRange):
        self.session.add(range)

    def get(self, range_id: int) -> Optional[VlanRestrictionRange]:
        return self.session.query(VlanRestrictionRange).filter_by(id=range_id).first()

    def get_by_range(self, core: Core, start: int, end: int) -> Optional[VlanRestrictionRange]:
        return self.session.query(VlanRestrictionRange).filter_by(
            core=core, _start=start, _end=end
        ).first()

    def list(self, core: Optional[Core] = None) -> list[type[VlanRestrictionRange]]:
        query = self.session.query(VlanRestrictionRange)
        if core:
            query = query.filter_by(core=core)
        return query.all()

    def delete(self, range: VlanRestrictionRange):
        self.session.delete(range)
