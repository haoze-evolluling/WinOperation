import ipaddress
from flask import Blueprint, request, jsonify
from services.network_mgmt import (
    get_network_status,
    toggle_wifi,
    set_dns,
    flush_dns_cache,
)

network_bp = Blueprint("network", __name__)


@network_bp.route("/api/network/status", methods=["GET"])
def network_status():
    adapters, connections = get_network_status()
    return jsonify({
        "success": True,
        "data": {
            "adapters": adapters,
            "connections": connections,
        },
    })


@network_bp.route("/api/network/wifi", methods=["POST"])
def wifi_toggle():
    data = request.get_json()
    action = data.get("action", "")

    if action not in ("enable", "disable"):
        return jsonify({"success": False, "message": "无效操作"}), 400

    ok, msg = toggle_wifi(action == "enable")
    if not ok:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "message": msg})


@network_bp.route("/api/network/dns", methods=["POST"])
def network_set_dns():
    data = request.get_json()
    adapter_name = data.get("adapter_name", "").strip()
    dns_servers = data.get("dns_servers", [])

    if not adapter_name:
        return jsonify({"success": False, "message": "请选择适配器"}), 400

    for ip in dns_servers:
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return jsonify({"success": False, "message": f"无效的 IP 地址: {ip}"}), 400

    ok, msg = set_dns(adapter_name, dns_servers)
    if not ok:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "message": msg})


@network_bp.route("/api/network/flushdns", methods=["POST"])
def flush_dns():
    ok, msg = flush_dns_cache()
    if not ok:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "message": msg})
