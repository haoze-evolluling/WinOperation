import subprocess
import winreg
from flask import Blueprint, jsonify
from utils import CREATE_NO_WINDOW

win11_bp = Blueprint("win11", __name__)

MENU_KEY = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
TASKBAR_PATH = (
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
)
SEARCH_PATH = r"Software\Policies\Microsoft\Windows\Explorer"


def _get_reg_dword(key_path, name):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
        val, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return val
    except FileNotFoundError:
        return None
    except Exception:
        return None


def _set_reg_dword(key_path, name, value):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0,
            winreg.KEY_SET_VALUE | winreg.KEY_CREATE_SUB_KEY,
        )
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
        winreg.CloseKey(key)
    except Exception:
        pass


def _delete_reg_value(key_path, name):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0,
            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,
        )
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    except Exception:
        pass


def _ensure_key(key_path):
    try:
        sub_key = ""
        parts = key_path.split("\\")
        for part in parts:
            sub_key = f"{sub_key}\\{part}" if sub_key else part
            try:
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key)
            except FileNotFoundError:
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, sub_key)
    except Exception:
        pass


# ─── 右键菜单 ───


@win11_bp.route("/api/win11/classic-menu", methods=["GET"])
def get_classic_menu():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            rf"{MENU_KEY}\InprocServer32",
        )
        winreg.CloseKey(key)
        enabled = True
    except FileNotFoundError:
        enabled = False
    except Exception:
        enabled = False
    return jsonify({"success": True, "data": {"enabled": enabled}})


@win11_bp.route("/api/win11/classic-menu/enable", methods=["POST"])
def enable_classic_menu():
    try:
        _ensure_key(rf"{MENU_KEY}\InprocServer32")
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            rf"{MENU_KEY}\InprocServer32",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)
        return jsonify({"success": True, "message": "已启用经典右键菜单，重启资源管理器后生效"})
    except Exception:
        return jsonify({"success": False, "message": "操作失败"}), 500


@win11_bp.route("/api/win11/classic-menu/disable", methods=["POST"])
def disable_classic_menu():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            MENU_KEY, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE,
        )
        winreg.DeleteKey(key, "InprocServer32")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return jsonify({"success": True, "message": "已恢复 Win11 默认右键菜单，重启资源管理器后生效"})


# ─── 任务栏对齐 ───


@win11_bp.route("/api/win11/taskbar-align", methods=["GET"])
def get_taskbar_align():
    val = _get_reg_dword(TASKBAR_PATH, "TaskbarAl")
    left = val == 0
    return jsonify({"success": True, "data": {"left": left}})


@win11_bp.route("/api/win11/taskbar-align/left", methods=["POST"])
def set_taskbar_left():
    _set_reg_dword(TASKBAR_PATH, "TaskbarAl", 0)
    return jsonify({"success": True, "message": "任务栏已左对齐，重启资源管理器后生效"})


@win11_bp.route("/api/win11/taskbar-align/center", methods=["POST"])
def set_taskbar_center():
    _set_reg_dword(TASKBAR_PATH, "TaskbarAl", 1)
    return jsonify({"success": True, "message": "任务栏已居中对齐，重启资源管理器后生效"})


# ─── 搜索建议 ───


@win11_bp.route("/api/win11/disable-search", methods=["GET"])
def get_disable_search():
    val = _get_reg_dword(SEARCH_PATH, "DisableSearchBoxSuggestions")
    return jsonify({"success": True, "data": {"enabled": val == 1}})


@win11_bp.route("/api/win11/disable-search/enable", methods=["POST"])
def enable_disable_search():
    _ensure_key(SEARCH_PATH)
    _set_reg_dword(SEARCH_PATH, "DisableSearchBoxSuggestions", 1)
    return jsonify({"success": True, "message": "已禁用搜索建议，重启资源管理器后生效"})


@win11_bp.route("/api/win11/disable-search/disable", methods=["POST"])
def disable_disable_search():
    _delete_reg_value(SEARCH_PATH, "DisableSearchBoxSuggestions")
    return jsonify({"success": True, "message": "已启用搜索建议，重启资源管理器后生效"})


# ─── 重启资源管理器 ───


@win11_bp.route("/api/win11/restart-explorer", methods=["POST"])
def restart_explorer():
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            capture_output=True, timeout=10, creationflags=CREATE_NO_WINDOW,
        )
        return jsonify({"success": True, "message": "资源管理器已重启"})
    except Exception:
        return jsonify({"success": False, "message": "重启失败"}), 500
