import subprocess
import winreg
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify
from utils import CREATE_NO_WINDOW

update_bp = Blueprint("update", __name__)

UPDATE_KEY = r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
POLICY_KEY = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
SERVICES = [
    ("wuauserv", "Windows Update"),
    ("UsoSvc", "Update Orchestrator Service"),
    ("bits", "Background Intelligent Transfer Service"),
]


def _get_reg_value(key_path, name):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        val, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return str(val)
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


def _set_reg_value(key_path, name, value, typ="String"):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, key_path, 0,
            winreg.KEY_SET_VALUE | winreg.KEY_CREATE_SUB_KEY,
        )
        if typ == "DWord":
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
        else:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
        winreg.CloseKey(key)
    except Exception:
        pass


def _remove_reg_value(key_path, name):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, key_path, 0,
            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,
        )
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    except Exception:
        pass


def _ensure_reg_path(key_path):
    try:
        sub_key = ""
        parts = key_path.split("\\")
        for part in parts:
            sub_key = f"{sub_key}\\{part}" if sub_key else part
            try:
                winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key)
            except FileNotFoundError:
                winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, sub_key)
    except Exception:
        pass


def _utc_to_local(utc_str):
    if not utc_str:
        return ""
    try:
        s = utc_str.replace("Z", "+0000")
        dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
        local_dt = dt.astimezone()
        return local_dt.strftime("%Y年%m月%d日 %H:%M:%S")
    except Exception:
        return utc_str


def _set_service_startup(name, start_type):
    """Set service startup type using sc.exe."""
    try:
        subprocess.run(
            ["sc", "config", name, f"start={start_type}"],
            capture_output=True, timeout=10, creationflags=CREATE_NO_WINDOW,
        )
    except Exception:
        pass


def _stop_service(name):
    try:
        subprocess.run(
            ["net", "stop", name, "/y"],
            capture_output=True, timeout=15, creationflags=CREATE_NO_WINDOW,
        )
    except Exception:
        pass


def _start_service(name):
    try:
        subprocess.run(
            ["net", "start", name],
            capture_output=True, timeout=15, creationflags=CREATE_NO_WINDOW,
        )
    except Exception:
        pass


@update_bp.route("/api/update/status", methods=["GET"])
def update_status():
    expiry = _get_reg_value(UPDATE_KEY, "PauseUpdatesExpiryTime")
    max_days = _get_reg_value(UPDATE_KEY, "FlightSettingsMaxPauseDays")
    start = _get_reg_value(UPDATE_KEY, "PauseUpdatesStartTime")
    return jsonify({
        "success": True,
        "data": {
            "paused": bool(expiry),
            "expiry_time": expiry,
            "expiry_time_local": _utc_to_local(expiry),
            "start_time": start,
            "start_time_local": _utc_to_local(start),
            "max_pause_days": max_days,
        },
    })


@update_bp.route("/api/update/delay", methods=["POST"])
def delay_updates():
    try:
        _ensure_reg_path(UPDATE_KEY)
        _ensure_reg_path(POLICY_KEY)

        _set_reg_value(UPDATE_KEY, "FlightSettingsMaxPauseDays", 10000, "DWord")

        utc_now = datetime.now(timezone.utc)
        expiry = utc_now + timedelta(days=10000)

        start_str = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        expiry_str = expiry.strftime("%Y-%m-%dT%H:%M:%SZ")
        _set_reg_value(UPDATE_KEY, "PauseUpdatesStartTime", start_str)
        _set_reg_value(UPDATE_KEY, "PauseUpdatesExpiryTime", expiry_str)

        _set_reg_value(POLICY_KEY, "NoAutoUpdate", 1, "DWord")
        _set_reg_value(POLICY_KEY, "AUOptions", 2, "DWord")

        for svc, _ in SERVICES:
            _set_service_startup(svc, "disabled")
            _stop_service(svc)

        local_expiry = _utc_to_local(expiry_str)
        return jsonify({
            "success": True,
            "message": f"Windows 更新已推迟 10000 天，到期时间: {local_expiry}",
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"操作失败: {str(e)}"}), 500


@update_bp.route("/api/update/restore", methods=["POST"])
def restore_updates():
    try:
        keys_to_remove = [
            (UPDATE_KEY, "FlightSettingsMaxPauseDays"),
            (UPDATE_KEY, "PauseUpdatesStartTime"),
            (UPDATE_KEY, "PauseUpdatesExpiryTime"),
            (POLICY_KEY, "NoAutoUpdate"),
            (POLICY_KEY, "AUOptions"),
        ]
        for path, name in keys_to_remove:
            _remove_reg_value(path, name)

        for svc, _ in SERVICES:
            _set_service_startup(svc, "auto")
            _start_service(svc)

        return jsonify({
            "success": True,
            "message": "Windows 更新已恢复默认设置",
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"还原失败: {str(e)}"}), 500
