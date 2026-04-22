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

from typing import Optional
from ipaddress import IPv4Network
from sqlalchemy import String, ForeignKey, Text, TypeDecorator, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class IPv4NetworkType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return str(value) if value is not None else value

    def process_result_value(self, value, dialect):
        return IPv4Network(value) if value is not None else value


class Core(Base):
    """Core is a network construct in with subnets are located."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    datacenter: Mapped[str] = mapped_column(String(255))
    _size: Mapped[int] = mapped_column("size", default=4096)
    group: Mapped[Optional[str]] = mapped_column(String(255), default=None)

    __tablename__ = "cores"
    __table_args__ = (UniqueConstraint('datacenter', 'name', name='_datacenter_core_uc'),)

    def __init__(self, datacenter: str, name: str, size: int = 4096, group: Optional[str] = None):
        self.datacenter = datacenter
        self.name = name
        self.size = size
        self.group = group

    def __repr__(self):
        return f'<Core {self.name} ({self.datacenter})>'

    def __hash__(self):
        return hash((self.name, self.datacenter))

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int):
        if 0 < value > 4096:
            raise ValueError("Core size must be between 1 and 4096")
        self._size = value


class VlanRestrictionRange(Base):
    """Vlan Restriction Range is a network construct preventing selection of VLAN within a given core"""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    core_id: Mapped[int] = mapped_column(ForeignKey("cores.id"))
    description: Mapped[str] = mapped_column(String(255))
    _start: Mapped[int] = mapped_column("start")
    _end: Mapped[int] = mapped_column("end")
    core: Mapped["Core"] = relationship()

    __tablename__ = "vlan_restriction_ranges"

    def __init__(self, core: Core, description: str, start: int, end: int):
        self.core = core
        self.description = description
        self._start = start
        self._end = end
        self._validate_range()

    def __repr__(self):
        return f'<VlanRestrictionRange {self.core.name} ({self.start}-{self.end})>'

    def __hash__(self):
        return hash((self.core.name, self.start, self.end))

    def __iter__(self):
        return iter(range(self.start, self.end + 1))

    def __contains__(self, item):
        return self.start <= item <= self.end

    def __len__(self):
        return self.end - self.start + 1

    def _validate_range(self):
        if not (1 <= self._start <= self._end <= self.core.size):
            raise ValueError(
                f'VLAN restriction range ({self._start}-{self._end}) is invalid for core size {self.core.size}. '
                'Start must be >= 1, End must be <= core size, and Start must be <= End.'
            )

    @property
    def start(self) -> int:
        return self._start

    @start.setter
    def start(self, value: int):
        if not (1 <= value <= self._end and value <= self.core.size):
            raise ValueError('Start must be between 1 and the core size and less than or equal to end.')
        self._start = value

    @property
    def end(self) -> int:
        return self._end

    @end.setter
    def end(self, value: int):
        if not (self._start <= value <= self.core.size):
            raise ValueError('End must be between the start and the core size.')
        self._end = value


class Vlan(Base):
    """VLAN is a network construct defining a subnet within a core"""

    core_id: Mapped[int] = mapped_column(ForeignKey("cores.id"))
    _number: Mapped[int] = mapped_column("number")
    subnet: Mapped[IPv4Network] = mapped_column(IPv4NetworkType(255))
    gcode: Mapped[str] = mapped_column(String(255))
    purpose: Mapped[str] = mapped_column(String(255))
    _name: Mapped[str] = mapped_column("name")
    core: Mapped["Core"] = relationship()
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)

    __tablename__ = "vlans"
    __table_args__ = (PrimaryKeyConstraint('number', 'core_id', name='_number_core_pc'),)

    def __init__(self, number: int, subnet: IPv4Network, core: Core, gcode: str, purpose: str,
                 name: Optional[str] = None, description: Optional[str] = None):
        self.core = core
        self.subnet = subnet
        self.gcode = gcode
        self.purpose = purpose
        self.number = number
        self.name = name
        self.description = description

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Vlan {self.core.name} {self.number}>'

    def __eq__(self, other):
        if not isinstance(other, Vlan):
            return False
        return self.number == other.number and self.core == other.core

    def __hash__(self):
        return hash((self.number, self.core))

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, number: int):
        if number <= 1:
            raise ValueError('Vlan number must be greater than 1')

        if number > self.core.size:
            raise ValueError('Vlan number exceeds core size')

        self._number = number

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        exclusion_map = str.maketrans(
            {
                ' ': '_',
                '-': '_'
            }
        )

        if name:
            self._name = name.translate(exclusion_map).upper()
        else:
            self._name = f'{self.subnet}_{self.gcode}_{self.purpose}'.translate(exclusion_map).upper()
