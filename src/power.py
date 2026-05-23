from flask import Blueprint, request, jsonify
from services.power_mgmt import (
    get_active_scheme_name,
    list_schemes,
    set_active_scheme,
    get_fast_startup_status,
    set_fast_startup,
)

power_bp = Blueprint("power", __name__)


@power_bp.route("/api/power/status", methods=["GET"])
def power_status():
    return jsonify({
        "success": True,
        "data": {
            "current_scheme": get_active_scheme_name(),
            "fast_startup": get_fast_startup_status(),
            "schemes": list_schemes(),
        },
    })


@power_bp.route("/api/power/scheme", methods=["POST"])
def set_scheme():
    data = request.get_json()
    scheme_guid = data.get("scheme_guid", "").strip()

    if not scheme_guid:
        return jsonify({"success": False, "message": "请选择电源方案"}), 400

    ok, msg = set_active_scheme(scheme_guid)
    if not ok:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "message": msg})


@power_bp.route("/api/power/faststartup", methods=["POST"])
def toggle_fast_startup():
    data = request.get_json()
    enable = data.get("enable", False)

    ok, msg = set_fast_startup(enable)
    if not ok:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "message": msg})
