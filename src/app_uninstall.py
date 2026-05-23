import subprocess
from flask import Blueprint, jsonify, request
from utils import CREATE_NO_WINDOW

app_uninstall_bp = Blueprint("app_uninstall", __name__)


@app_uninstall_bp.route("/api/app-uninstall/uninstall", methods=["POST"])
def uninstall_app():
    data = request.get_json() or {}
    command = data.get("command", "")
    label = data.get("label", "")
    if not command:
        return jsonify({"success": False, "message": "缺少卸载命令"})

    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True, text=False, timeout=60,
            creationflags=CREATE_NO_WINDOW,
        )
        stdout = result.stdout.decode("utf-8", errors="replace").strip()
        if result.returncode == 0:
            return jsonify({"success": True, "message": f"「{label}」卸载成功"})
        error_msg = stdout or "未知错误"
        return jsonify({"success": False, "message": f"卸载失败: {error_msg}"})
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "message": "卸载命令执行超时"})
    except Exception as e:
        return jsonify({"success": False, "message": f"卸载异常: {str(e)}"})
