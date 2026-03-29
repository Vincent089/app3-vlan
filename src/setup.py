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
from setuptools import setup

setup(
    name='vlan-manager',
    version='0.1.0',
    author='Vincent Corriveau',
    author_email='vincent.corriveau89@gmail.com',
    description='A network construct management application for VLANs and Cores',
    packages=['app'],
    python_requires='>=3.7',
)
