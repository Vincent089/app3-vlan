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

from dataclasses import dataclass
from ipaddress import IPv4Network


@dataclass(unsafe_hash=True)
class Datacenter:
    """Datacenter is a network construct representing a virtual datacenter"""
    name: str


@dataclass(unsafe_hash=True)
class Core:
    """Core is a network construct in with subnets are located."""
    datacenter: Datacenter
    name: str
    size: int = 4096
    group: str = None


class VlanRestrictionRange:
    """Vlan Restriction Range is a network construct preventing selection of VLAN within a given core"""

    _start = 1

    def __init__(self, core: Core, description: str, start: int, end: int):
        self.core = core
        self.description = description
        self._end = core.size
        self.start = start
        self.end = end

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

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        if 1 > start or start > self.end or start > self.core.size:
            raise ValueError('Start must be between 1 and the core size)')

        self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        if end < self.start or end > self.core.size:
            raise ValueError('End must be between the start and the core size')

        self._end = end


class Vlan:
    """VLAN is a network construct defining a subnet within a core"""

    _number = None
    _name = None

    def __init__(self, number: int, subnet: IPv4Network, core: Core, gcode: str, purpose: str,
                 name: str = None, description: str = None):

        self.core = core
        self.number = number
        self.subnet = subnet
        self.gcode = gcode
        self.purpose = purpose
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
    def number(self):
        return self._number

    @number.setter
    def number(self, number: int):
        if number <= 1:
            raise ValueError('Vlan number must be greater than 1')

        if number > self.core.size:
            raise ValueError('Vlan number exceeds core size')

        self._number = number

    @property
    def name(self):
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
