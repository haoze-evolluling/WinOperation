import ctypes
import uuid
import subprocess
import winreg
from ctypes import wintypes
from utils import CREATE_NO_WINDOW

_powrprof = ctypes.windll.powrprof

_PowerGetActiveScheme = _powrprof.PowerGetActiveScheme
_PowerGetActiveScheme.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p)]
_PowerGetActiveScheme.restype = wintypes.DWORD

_PowerSetActiveScheme = _powrprof.PowerSetActiveScheme
_PowerSetActiveScheme.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
_PowerSetActiveScheme.restype = wintypes.DWORD

_LocalFree = ctypes.windll.kernel32.LocalFree
_LocalFree.argtypes = [wintypes.HANDLE]
_LocalFree.restype = wintypes.HANDLE

_NULL = ctypes.c_void_p(0)

# 已知电源方案 GUID → 中文名称
KNOWN_SCHEMES = {
    "381b4222-f694-41f0-9685-ff5bb260df2e": "平衡",
    "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c": "高性能",
    "a1841308-3541-4fab-bc81-f71556f20b4a": "节能",
    "e9a42b02-d5df-448d-aa00-03f14749eb61": "卓越性能",
    "961cc777-2547-4192-996d-3740de0dcf3a": "更好电池续航叠加方案",
    "ded574b5-4e0d-4ef4-a739-dfa47bc5ef2a": "高性能叠加方案",
    "2d5835bc-bc12-4ebc-9e2a-1e9de5e7e6f3": "最大性能叠加方案",
}


def _guid_ptr_to_str(guid_ptr):
    """Read a GUID from a pointer returned by PowerGetActiveScheme."""
    buf = (ctypes.c_byte * 16).from_address(guid_ptr)
    return str(uuid.UUID(bytes_le=bytes(buf))).lower()


def _scheme_name(guid_str):
    """Look up Chinese name for a scheme GUID; fall back to registry, then '未知方案'."""
    if guid_str in KNOWN_SCHEMES:
        return KNOWN_SCHEMES[guid_str]
    # Fallback: look up via registry
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            rf"SYSTEM\CurrentControlSet\Control\Power\User\PowerSchemes\{guid_str}",
        )
        name_raw, _ = winreg.QueryValueEx(key, "FriendlyName")
        winreg.CloseKey(key)
        name = name_raw.split(",")[-1] if "," in name_raw else name_raw
        return name.strip()
    except Exception:
        pass
    return "未知方案"


def get_active_scheme_name():
    """Return the Chinese name of the currently active power scheme."""
    try:
        scheme_ptr = ctypes.c_void_p()
        ret = _PowerGetActiveScheme(_NULL, ctypes.byref(scheme_ptr))
        if ret != 0:
            return ""
        guid_str = _guid_ptr_to_str(scheme_ptr.value)
        _LocalFree(scheme_ptr)
        return _scheme_name(guid_str)
    except Exception:
        pass
    return ""


def list_schemes():
    """Return list of dicts: [{'guid': '{...}', 'name': '中文名称'}, ...]"""
    return [
        {"guid": "{" + guid + "}", "name": name}
        for guid, name in KNOWN_SCHEMES.items()
    ]


_ERR_MSG = {
    50: "当前系统不支持此电源方案",
    87: "当前系统不支持此电源方案",
    5: "权限不足，请以管理员身份运行",
}


def set_active_scheme(guid_str: str):
    """Set the active power scheme by GUID. Returns (success: bool, message: str)."""
    try:
        guid_str_clean = guid_str.strip().strip("{}")
        guid = uuid.UUID(guid_str_clean)
        buf = (ctypes.c_byte * 16)()
        ctypes.memmove(buf, guid.bytes_le, 16)
        ret = _PowerSetActiveScheme(_NULL, ctypes.cast(ctypes.pointer(buf), ctypes.c_void_p))
        if ret == 0:
            return (True, "电源方案已切换")
        msg = _ERR_MSG.get(ret, f"切换电源方案失败 (错误码: {ret})")
        return (False, msg)
    except Exception as e:
        return (False, f"切换电源方案失败: {e}")


def get_fast_startup_status():
    """Return True if fast startup is enabled."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Power",
        )
        val, _ = winreg.QueryValueEx(key, "HiberbootEnabled")
        winreg.CloseKey(key)
        return val == 1
    except FileNotFoundError:
        return False
    except Exception:
        return False


def set_fast_startup(enable: bool):
    """Enable or disable fast startup. Returns (success: bool, message: str)."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Power",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "HiberbootEnabled", 0, winreg.REG_DWORD, 1 if enable else 0)
        winreg.CloseKey(key)

        action = "on" if enable else "off"
        result = subprocess.run(
            ["powercfg", "/h", action], capture_output=True,
            timeout=15, creationflags=CREATE_NO_WINDOW
        )
        if result.returncode != 0:
            return (False, f"{'启用' if enable else '禁用'}快速启动失败")

        label = "已启用" if enable else "已禁用"
        return (True, f"快速启动{label}")
    except Exception as e:
        return (False, f"操作失败: {e}")
