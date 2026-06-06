import ipaddress
import socket
import time
from flask import Blueprint, request, jsonify
from services.network_mgmt import (
    get_network_status,
    toggle_wifi,
    set_dns,
    flush_dns_cache,
)

network_bp = Blueprint("network", __name__)


def _resolve_target(target):
    started = time.perf_counter()
    infos = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    addresses = []
    seen = set()
    for family, _, _, _, sockaddr in infos:
        ip = sockaddr[0]
        if ip in seen:
            continue
        seen.add(ip)
        addresses.append({
            "ip": ip,
            "family": "IPv6" if family == socket.AF_INET6 else "IPv4",
        })
    return addresses, elapsed_ms


def _tcp_check(target, port, timeout=1.2):
    started = time.perf_counter()
    try:
        with socket.create_connection((target, port), timeout=timeout):
            elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
            return {"port": port, "open": True, "elapsed_ms": elapsed_ms, "error": ""}
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        return {"port": port, "open": False, "elapsed_ms": elapsed_ms, "error": str(exc)}


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


@network_bp.route("/api/network/diagnostics", methods=["POST"])
def network_diagnostics():
    data = request.get_json() or {}
    target = (data.get("target") or "www.baidu.com").strip()
    ports = data.get("ports") or [80, 443]

    if not target:
        return jsonify({"success": False, "message": "请输入诊断目标"}), 400

    clean_ports = []
    for port in ports[:4]:
        try:
            port_int = int(port)
        except (TypeError, ValueError):
            continue
        if 1 <= port_int <= 65535:
            clean_ports.append(port_int)
    if not clean_ports:
        clean_ports = [80, 443]

    try:
        addresses, elapsed_ms = _resolve_target(target)
        dns_error = ""
    except Exception as exc:
        addresses, elapsed_ms, dns_error = [], 0, str(exc)

    tcp_checks = [_tcp_check(target, port) for port in clean_ports]

    return jsonify({
        "success": True,
        "data": {
            "target": target,
            "resolved_ips": addresses,
            "elapsed_ms": elapsed_ms,
            "dns_error": dns_error,
            "tcp_checks": tcp_checks,
            "online": bool(addresses) or any(item["open"] for item in tcp_checks),
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
