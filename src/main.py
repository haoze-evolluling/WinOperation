import ctypes
import json as _json
import os
import platform
import subprocess
import sys
import threading
import time

import re as _re
import urllib.request
import webbrowser
from flask import Flask, Blueprint, jsonify, render_template, request
from models import db
from config import Config, BASE_DIR, RESOURCE_DIR
from network import network_bp
from power import power_bp
from scheduler import scheduler_bp
from speedtest import speedtest_bp
from quick_settings import quick_bp
from activation import activation_bp
from update import update_bp
from app_uninstall import app_uninstall_bp
from win11 import win11_bp
from utils import CREATE_NO_WINDOW
from services.system_info import (
    get_boot_time_str,
    get_uptime_str,
    get_cpu_name,
    get_cpu_cores,
    get_cpu_frequency,
    get_cpu_usage,
    get_memory,
    get_swap,
    get_disks,
    get_top_processes,
    get_battery,
)
from services.gpu_info import get_gpu_names, get_gpu_detail

system_bp = Blueprint("system", __name__)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(RESOURCE_DIR, "templates"),
        static_folder=os.path.join(RESOURCE_DIR, "static"),
    )
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(network_bp)
    app.register_blueprint(power_bp)
    app.register_blueprint(scheduler_bp)
    app.register_blueprint(speedtest_bp)
    app.register_blueprint(quick_bp)
    app.register_blueprint(activation_bp)
    app.register_blueprint(update_bp)
    app.register_blueprint(app_uninstall_bp)
    app.register_blueprint(win11_bp)
    app.register_blueprint(system_bp)

    @app.route("/")
    def index():
        return render_template("dashboard.html")

    return app


@system_bp.route("/api/system/info", methods=["GET"])
def system_info():
    hostname = platform.node()
    os_ver = f"{platform.system()} {platform.release()} ({platform.version()})"
    login_user = os.environ.get("USERNAME", "")
    arch = os.environ.get("PROCESSOR_ARCHITECTURE", "")
    uptime_str = get_uptime_str()
    boot_time_str = get_boot_time_str()
    return jsonify({
        "success": True,
        "data": {
            "os": os_ver,
            "hostname": hostname,
            "uptime": uptime_str,
            "boot_time": boot_time_str,
            "login_user": login_user,
            "architecture": arch,
        },
    })



@system_bp.route("/api/system/hardware", methods=["GET"])
def system_hardware():
    current_freq, max_freq = get_cpu_frequency()
    data = {
        "cpu": get_cpu_name(),
        "gpus": get_gpu_names(),
        "cpu_cores": get_cpu_cores(),
        "cpu_current_freq": current_freq,
        "cpu_base_freq": max_freq,
        "cpu_max_freq": max_freq,
    }
    return jsonify({"success": True, "data": data})


@system_bp.route("/api/system/resources", methods=["GET"])
def system_resources():
    ram_total, ram_used, ram_available, ram_percent = get_memory()
    swap_total, swap_used, swap_percent = get_swap()

    disks = get_disks()
    disk_total = round(sum(d["total"] for d in disks), 1)
    disk_free = round(sum(d["free"] for d in disks), 1)
    disk_used = round(disk_total - disk_free, 1)
    disk_percent = round((1 - disk_free / disk_total) * 100, 1) if disk_total > 0 else 0

    data = {
        "cpu_usage": get_cpu_usage(),
        "ram_total": ram_total,
        "ram_used": ram_used,
        "ram_available": ram_available,
        "ram_percent": ram_percent,
        "swap_total": swap_total,
        "swap_used": swap_used,
        "swap_percent": swap_percent,
        "disk_total": disk_total,
        "disk_used": disk_used,
        "disk_free": disk_free,
        "disk_percent": disk_percent,
        "disks": disks,
        "top_processes": get_top_processes(5),
    }
    return jsonify({"success": True, "data": data})


@system_bp.route("/api/system/public-ip", methods=["GET"])
def system_public_ip():
    ip = None
    sources = [
        ("https://api.ipify.org?format=json", "ip"),
        ("https://ip.sb/json", "ip"),
    ]
    for url, key in sources:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=5)
            body = resp.read().decode("utf-8")
            data = _json.loads(body)
            ip = data.get(key, "")
            if ip:
                break
        except Exception:
            continue

    return jsonify({"success": True, "data": {"ip": ip or ""}})


@system_bp.route("/api/system/gpu-detail", methods=["GET"])
def system_gpu_detail():
    data = get_gpu_detail()
    return jsonify({"success": True, "data": data})


@system_bp.route("/api/system/battery", methods=["GET"])
def system_battery():
    return jsonify({"success": True, "data": get_battery()})


@system_bp.route("/api/system/temps", methods=["GET"])
def system_temps():
    result = {"cpu_temp": None, "gpu_temp": None}
    try:
        temps = psutil.sensors_temperatures()
        # Common keys: 'coretemp', 'k10temp', 'zenpower', 'acpitz' for CPU
        # GPU typically under 'amdgpu', 'nvidia', or similar
        for name, entries in temps.items():
            name_lower = name.lower()
            if not entries:
                continue
            avg = round(sum(s.current for s in entries) / len(entries), 1)
            if any(kw in name_lower for kw in ("cpu", "core", "k10", "zen", "package")):
                result["cpu_temp"] = avg
            elif any(kw in name_lower for kw in ("gpu", "amdgpu", "nvidia")):
                result["gpu_temp"] = avg
    except Exception:
        pass
    return jsonify({"success": True, "data": result})


@system_bp.route("/api/system/wifi-detail", methods=["GET"])
def system_wifi_detail():
    result = {"ssid": "", "signal": 0, "connected": False}
    try:
        out = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10, creationflags=CREATE_NO_WINDOW).stdout
        for line in out.splitlines():
            stripped = line.strip()
            if stripped.startswith("SSID"):
                parts = stripped.split(":", 1)
                if len(parts) > 1:
                    val = parts[1].strip()
                    if val:
                        result["ssid"] = val
                        result["connected"] = True
            if stripped.startswith("信号"):
                parts = stripped.split(":", 1)
                if len(parts) > 1:
                    try:
                        result["signal"] = int(parts[1].strip().rstrip("%"))
                    except Exception:
                        pass
            if stripped.startswith("State"):
                parts = stripped.split(":", 1)
                if len(parts) > 1:
                    result["connected"] = parts[1].strip() == "connected"
    except Exception:
        pass
    return jsonify({"success": True, "data": result})


@system_bp.route("/api/system/latency", methods=["GET"])
def system_latency():
    result = {"latency_ms": None, "loss_rate": None}
    try:
        out = subprocess.run(["ping", "-n", "1", "223.5.5.5"], capture_output=True, text=True, timeout=10, creationflags=CREATE_NO_WINDOW).stdout
        ms_match = _re.search(r"时间[=<]\s*(\d+)\s*ms", out)
        if not ms_match:
            ms_match = _re.search(r"Average\s*=\s*(\d+)ms", out)
        if ms_match:
            result["latency_ms"] = int(ms_match.group(1))
        loss_match = _re.search(r"\((\d+)%", out)
        if loss_match:
            result["loss_rate"] = int(loss_match.group(1))
    except Exception:
        pass
    return jsonify({"success": True, "data": result})


@system_bp.route("/api/system/gateway-delay", methods=["GET"])
def system_gateway_delay():
    """获取到默认网关的 ping 延迟（ms）。"""
    result = {"gateway": "", "delay_ms": None, "error": None}
    try:
        out = subprocess.run(
            ["route", "print"], capture_output=True, text=True,
            timeout=10, creationflags=CREATE_NO_WINDOW,
        ).stdout
        # 匹配默认网关: 0.0.0.0 0.0.0.0 <gateway_ip>
        match = _re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", out)
        if not match:
            result["error"] = "未找到默认网关"
            return jsonify({"success": True, "data": result})

        gateway = match.group(1)
        result["gateway"] = gateway

        ping_out = subprocess.run(
            ["ping", "-n", "1", gateway], capture_output=True, text=True,
            timeout=10, creationflags=CREATE_NO_WINDOW,
        ).stdout

        ms_match = _re.search(r"时间[=<]\s*(\d+)\s*ms", ping_out)
        if not ms_match:
            ms_match = _re.search(r"Average\s*=\s*(\d+)ms", ping_out)
        if ms_match:
            result["delay_ms"] = int(ms_match.group(1))
        else:
            result["error"] = "请求超时"
    except Exception as e:
        result["error"] = str(e)

    return jsonify({"success": True, "data": result})


@system_bp.route("/api/system/exit", methods=["POST"])
def system_exit():
    def _exit():
        time.sleep(1)
        marker = os.path.join(BASE_DIR, ".exit_marker")
        try:
            open(marker, "w").close()
        except Exception:
            pass
        os._exit(0)
    threading.Thread(target=_exit, daemon=True).start()
    return jsonify({"success": True, "message": "程序即将退出"})


def run_server():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    app = create_app()

    with app.app_context():
        db.create_all()

    webbrowser.open("http://127.0.0.1:2233")

    app.run(host="127.0.0.1", port=2233, debug=False)


def elevate_and_run():
    exe = sys.executable if getattr(sys, "frozen", False) else sys.argv[0]
    try:
        subprocess.run(
            ["powershell", "-Command", f'Start-Process "{exe}" -Verb RunAs'],
            check=True,
            creationflags=CREATE_NO_WINDOW,
        )
    except Exception:
        print("错误: 无法自动提权，请右键以管理员身份运行")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    if not is_admin():
        elevate_and_run()

    run_server()
