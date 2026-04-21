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
from app.services import DatacenterService, CoreService, VlanService
from app.schemas import DatacenterSchema, CoreSchema, VlanSchema

datacenters_bp = Blueprint("datacenters", __name__)
datacenter_service = DatacenterService()
datacenter_schema = DatacenterSchema()

cores_bp = Blueprint("cores", __name__)
core_service = CoreService()
core_schema = CoreSchema()

vlans_bp = Blueprint("vlans", __name__)
vlan_service = VlanService()
vlan_schema = VlanSchema()


@datacenters_bp.route("/", methods=["GET"])
def list_datacenters():
    datacenters = datacenter_service.list_datacenters()
    return jsonify(datacenter_schema.dump(datacenters, many=True)), 200


@datacenters_bp.route("/", methods=["POST"])
def create_datacenter():
    data = request.get_json()
    errors = datacenter_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    datacenter = datacenter_service.create_datacenter(data["name"])
    return jsonify(datacenter_schema.dump(datacenter)), 201


@datacenters_bp.route("/<int:datacenter_id>", methods=["GET"])
def get_datacenter(datacenter_id):
    datacenter = datacenter_service.get_datacenter(datacenter_id)
    if not datacenter:
        return jsonify({"error": "Datacenter not found"}), 404

    return jsonify(datacenter_schema.dump(datacenter)), 200


@datacenters_bp.route("/<int:datacenter_id>", methods=["PUT"])
def update_datacenter(datacenter_id):
    data = request.get_json()
    errors = datacenter_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    datacenter = datacenter_service.update_datacenter(datacenter_id, data.get("name"))
    if not datacenter:
        return jsonify({"error": "Datacenter not found"}), 404

    return jsonify(datacenter_schema.dump(datacenter)), 200


@datacenters_bp.route("/<int:datacenter_id>", methods=["DELETE"])
def delete_datacenter(datacenter_id):
    if datacenter_service.delete_datacenter(datacenter_id):
        return "", 204

    return jsonify({"error": "Datacenter not found"}), 404


@cores_bp.route("/", methods=["GET"])
def list_cores():
    datacenter_id = request.args.get("datacenter_id", type=int)
    cores = core_service.list_cores(datacenter_id)
    return jsonify(core_schema.dump(cores, many=True)), 200


@cores_bp.route("/", methods=["POST"])
def create_core():
    data = request.get_json()
    errors = core_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    core = core_service.create_core(
        datacenter_id=data["datacenter_id"],
        name=data["name"],
        size=data.get("size", 4096),
        group=data.get("group")
    )
    return jsonify(core_schema.dump(core)), 201


@cores_bp.route("/<int:core_id>", methods=["GET"])
def get_core(core_id):
    core = core_service.get_core(core_id)
    if not core:
        return jsonify({"error": "Core not found"}), 404

    return jsonify(core_schema.dump(core)), 200


@cores_bp.route("/<int:core_id>", methods=["PUT"])
def update_core(core_id):
    data = request.get_json()
    errors = core_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    core = core_service.update_core(
        core_id,
        name=data.get("name"),
        size=data.get("size"),
        group=data.get("group")
    )
    if not core:
        return jsonify({"error": "Core not found"}), 404

    return jsonify(core_schema.dump(core)), 200


@cores_bp.route("/<int:core_id>", methods=["DELETE"])
def delete_core(core_id):
    if core_service.delete_core(core_id):
        return "", 204

    return jsonify({"error": "Core not found"}), 404


@vlans_bp.route("/", methods=["GET"])
def list_vlans():
    core_id = request.args.get("core_id", type=int)
    vlans = vlan_service.list_vlans(core_id)
    return jsonify(vlan_schema.dump(vlans, many=True)), 200


@vlans_bp.route("/<int:vlan_id>", methods=["GET"])
def get_vlan(vlan_id):
    vlan = vlan_service.get_vlan(vlan_id)
    if not vlan:
        return jsonify({"error": "Vlan not found"}), 404

    return jsonify(vlan_schema.dump(vlan)), 200
