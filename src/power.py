from flask import Blueprint, request, jsonify
import psutil
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


@power_bp.route("/api/power/battery-insights", methods=["GET"])
def battery_insights():
    battery = None
    try:
        battery = psutil.sensors_battery()
    except Exception:
        battery = None

    current_scheme = get_active_scheme_name()
    fast_startup = get_fast_startup_status()

    if battery is None:
        return jsonify({
            "success": True,
            "data": {
                "present": False,
                "percentage": 0,
                "charging": False,
                "remaining_label": "无电池",
                "status": "台式机/未检测到电池",
                "tips": [
                    "未检测到电池，电源建议以性能与启动策略为主。",
                    "当前电源方案可按工作负载切换为平衡或高性能。",
                ],
                "current_scheme": current_scheme,
                "fast_startup": fast_startup,
            },
        })

    secsleft = getattr(battery, "secsleft", None)
    if isinstance(secsleft, (int, float)) and 0 < secsleft < 10 ** 8:
        hours = int(secsleft // 3600)
        minutes = int((secsleft % 3600) // 60)
        remaining_label = f"{hours} 小时 {minutes} 分钟"
    else:
        remaining_label = "系统未提供"

    tips = []
    if battery.power_plugged:
        tips.append("当前已接入电源，可使用高性能方案处理重负载任务。")
    elif battery.percent < 25:
        tips.append("电池电量偏低，建议接入电源或切换节能方案。")
    elif battery.percent < 50:
        tips.append("电池电量中等，建议减少后台任务并保持平衡方案。")
    else:
        tips.append("电池余量充足，可保持当前方案并继续观察续航。")

    if fast_startup:
        tips.append("快速启动已启用，适合日常开机速度优先。")
    else:
        tips.append("快速启动已禁用，适合需要完整冷启动排障的场景。")

    status = "充电中" if battery.power_plugged else "电池供电"
    return jsonify({
        "success": True,
        "data": {
            "present": True,
            "percentage": round(battery.percent),
            "charging": bool(battery.power_plugged),
            "remaining_label": remaining_label,
            "status": status,
            "tips": tips,
            "current_scheme": current_scheme,
            "fast_startup": fast_startup,
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
