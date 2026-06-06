import subprocess
from flask import Blueprint, request, jsonify

quick_bp = Blueprint("quick", __name__)

QUICK_COMMANDS = {
    # 系统核心配置
    "control_panel": "control",
    "local_group_policy": "gpedit.msc",
    "msconfig": "msconfig",
    # 硬件与磁盘管理
    "device_manager": "devmgmt.msc",
    "disk_management": "diskmgmt.msc",
    "dxdiag": "dxdiag",
    "system_info": "msinfo32",
    # 网络与远程管理
    "network_connections": "ncpa.cpl",
    "network_sharing_center": "control /name Microsoft.NetworkAndSharingCenter",
    "remote_desktop": "mstsc",
    "resource_monitor": "resmon",
    # 系统状态与监控
    "task_manager": "taskmgr",
    "event_viewer": "eventvwr.msc",
    "perfmon": "perfmon",
    # 更新与应用管理
    "windows_update": "start ms-settings:windowsupdate",
    "apps_features": "start ms-settings:appsfeatures",
    "programs_features": "appwiz.cpl",
    # 电源、显示与个性化
    "power_options": "powercfg.cpl",
    "display_settings": "start ms-settings:display",
    "mouse_keyboard": "control mouse",
    # 系统维护与安全
    "system_properties": "sysdm.cpl",
    "firewall": "wf.msc",
    "registry_editor": "regedit",
    "services": "services.msc",
    "computer_management": "compmgmt.msc",
    "user_accounts": "netplwiz",
    "disk_cleanup": "cleanmgr",
    "defrag": "dfrgui",
    "system_restore": "rstrui",
    "windows_security": "start windowsdefender:",
    "credential_manager": "control /name Microsoft.CredentialManager",
    # 命令与快捷工具
    "cmd_prompt": "start cmd",
    "powershell": "start powershell",
}


@quick_bp.route("/api/quick/launch", methods=["POST"])
def launch():
    data = request.get_json()
    command_id = data.get("command_id", "").strip()

    if command_id not in QUICK_COMMANDS:
        return jsonify({"success": False, "message": "无效的命令 ID"}), 400

    cmd = QUICK_COMMANDS[command_id]
    try:
        subprocess.Popen(["cmd", "/c", cmd])
    except Exception as e:
        return jsonify({"success": False, "message": f"启动失败: {str(e)}"}), 500

    return jsonify({"success": True, "message": f"已启动: {command_id}"})
