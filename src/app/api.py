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
from flask import Blueprint, jsonify, request
from app.services import CoreService, VlanService
from app.schemas import CoreSchema, VlanSchema

cores_bp = Blueprint("cores", __name__)
core_service = CoreService()
core_schema = CoreSchema()

vlans_bp = Blueprint("vlans", __name__)
vlan_service = VlanService()
vlan_schema = VlanSchema()


@cores_bp.route("/", methods=["GET"])
def list_cores():
    datacenter = request.args.get("datacenter", type=str)
    cores = core_service.list_cores(datacenter)

    return jsonify(core_schema.dump(cores, many=True)), 200


@cores_bp.route("/", methods=["POST"])
def create_core():
    data = request.get_json()
    errors = core_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    core = core_service.create_core(
            datacenter=data.get("datacenter"),
            name=data.get("name"),
            size=data.get("size", 4096),
            group=data.get("group")
    )

    return jsonify(core_schema.dump(core)), 201


@cores_bp.route("/<int:core_id>", methods=["GET"])
def get_core(core_id):
    core = core_service.get_core(core_id)
    if not core:
        return jsonify({ "error": "Core not found" }), 404

    return jsonify(core_schema.dump(core)), 200


@cores_bp.route("/<int:core_id>", methods=["PATCH"])
def update_core(core_id):
    data = request.get_json()
    errors = core_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    core = core_service.update_core(
            core_id,
            name=data.get("name"),
            group=data.get("group")
    )
    if not core:
        return jsonify({ "error": "Core not found" }), 404

    return jsonify(core_schema.dump(core)), 200


@cores_bp.route("/<int:core_id>/vlans", methods=["GET"])
def list_core_vlans(core_id):
    vlans = vlan_service.list_vlans(core_id)

    return jsonify(vlan_schema.dump(vlans, many=True)), 200


@cores_bp.route("/<int:core_id>/vlans", methods=["POST"])
def create_core_vlan(core_id):
    data = request.get_json()
    errors = vlan_schema.validate(data, partial=('core_id',))
    if errors:
        return jsonify(errors), 400

    vlan = vlan_service.create_vlan(
            number=data.get('number'),
            subnet=data.get('subnet'),
            core_id=core_id,
            gcode=data.get('gcode'),
            purpose=data.get('purpose'),
            name=data.get('name'),
            description=data.get('description')
    )

    return jsonify(vlan_schema.dump(vlan)), 201


@cores_bp.route("/<int:core_id>/vlans/<int:vlan_number>", methods=["GET"])
def get_core_vlan(core_id, vlan_number):
    vlan = vlan_service.get_vlan_by_number(core_id, vlan_number)

    if not vlan:
        return jsonify({ "error": "Vlan not found" }), 404

    return jsonify(vlan_schema.dump(vlan)), 200


@cores_bp.route("/<int:core_id>/vlans/<int:vlan_number>", methods=["PATCH"])
def update_core_vlan(core_id, vlan_number):
    data = request.get_json()
    errors = vlan_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    vlan = vlan_service.update_vlan(
            core_id=core_id,
            number=vlan_number,
            name=data.get('name'),
            description=data.get('description'),
            gcode=data.get('gcode'),
            purpose=data.get('purpose')
    )

    if not vlan:
        return jsonify({ "error": "Vlan not found" }), 404

    return jsonify(vlan_schema.dump(vlan)), 200


@cores_bp.route("/<int:core_id>/vlans/<int:vlan_number>", methods=["DELETE"])
def delete_core_vlan(core_id, vlan_number):
    vlan = vlan_service.delete_vlan(core_id=core_id, number=vlan_number)

    if vlan is None:
        return jsonify({ "error": "Vlan not found" }), 404

    return { }, 204


@vlans_bp.route("/", methods=["GET"])
def list_vlans():
    core_id = request.args.get("core_id", type=int)
    vlans = vlan_service.list_vlans(core_id)

    return jsonify(vlan_schema.dump(vlans, many=True)), 200


@vlans_bp.route("/", methods=["POST"])
def create_vlan():
    data = request.get_json()
    errors = vlan_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    vlan = vlan_service.create_vlan(
            number=data.get('number'),
            subnet=data.get('subnet'),
            core_id=data.get('core_id'),
            gcode=data.get('gcode'),
            purpose=data.get('purpose'),
            name=data.get('name'),
            description=data.get('description')
    )

    return jsonify(vlan_schema.dump(vlan)), 201


@vlans_bp.route("/<uuid:vlan_id>", methods=["GET"])
def get_vlan(vlan_id):
    vlan = vlan_service.get_vlan(vlan_id)
    if not vlan:
        return jsonify({ "error": "Vlan not found" }), 404

    return jsonify(vlan_schema.dump(vlan)), 200


@vlans_bp.route("/<uuid:vlan_id>", methods=["PATCH"])
def update_core_vlan(vlan_id):
    data = request.get_json()
    errors = vlan_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    vlan = vlan_service.update_vlan(
            vlan_id=vlan_id,
            name=data.get('name'),
            description=data.get('description'),
            gcode=data.get('gcode'),
            purpose=data.get('purpose')
    )

    if not vlan:
        return jsonify({ "error": "Vlan not found" }), 404

    return jsonify(vlan_schema.dump(vlan)), 200


@vlans_bp.route("/<uuid:vlan_id>", methods=["DELETE"])
def delete_vlan(vlan_id):
    vlan = vlan_service.delete_vlan(vlan_id=vlan_id)

    if vlan is None:
        return jsonify({ "error": "Vlan not found" }), 404

    return { }, 204
