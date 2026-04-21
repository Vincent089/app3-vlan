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
from app.db import SessionLocal
from app.repository import CoreRepository, VlanRepository, VlanRestrictionRangeRepository

class UnitOfWork:

    def __init__(self):
        self.session_factory = SessionLocal

    def __enter__(self):
        self.session = self.session_factory()

        self.cores = CoreRepository(self.session)
        self.vlans = VlanRepository(self.session)
        self.ranges = VlanRestrictionRangeRepository(self.session)

        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.rollback()
        else:
            self.commit()

        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
