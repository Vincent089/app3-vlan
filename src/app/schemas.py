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
from marshmallow import Schema, fields

class CoreSchema(Schema):
    id = fields.Int(dump_only=True)
    datacenter = fields.String(required=True)
    name = fields.Str(required=True)
    size = fields.Int()
    group = fields.Str(allow_none=True)

class VlanSchema(Schema):
    id = fields.UUID(dump_only=True)
    core_id = fields.Int(required=True)
    number = fields.Int()
    subnet = fields.Str(required=True)
    gcode = fields.Str(required=True)
    purpose = fields.Str(required=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)

class VlanRestrictionRangeSchema(Schema):
    id = fields.Int(dump_only=True)
    core_id = fields.Int(required=True)
    description = fields.Str(required=True)
    start = fields.Int(required=True)
    end = fields.Int(required=True)
