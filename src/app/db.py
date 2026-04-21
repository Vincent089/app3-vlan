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
import os
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "app.db")


class Base(DeclarativeBase):
    def to_dict(self, include=None, exclude=None):
        mapper = inspect(self)

        data = {}

        for column in mapper.mapper.column_attrs:
            key = column.key

            if include and key not in include:
                continue

            if exclude and key in exclude:
                continue

            data[key] = getattr(self, key)

        return data


engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

SessionLocal = scoped_session(
    sessionmaker(bind=engine, expire_on_commit=False)
)


def init_db():
    from app import models  # noqa

    Base.metadata.create_all(bind=engine)
