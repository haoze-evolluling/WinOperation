import os
import subprocess
from flask import Blueprint, request, jsonify
from utils import CREATE_NO_WINDOW

activation_bp = Blueprint("activation", __name__)


def _run_slmgr(args_str):
    try:
        result = subprocess.run(
            ["cscript", os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "slmgr.vbs")]
            + args_str.split(),
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
            creationflags=CREATE_NO_WINDOW,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return True, output
    except subprocess.TimeoutExpired:
        return False, "命令执行超时"
    except Exception as e:
        return False, f"执行失败: {str(e)}"


@activation_bp.route("/api/activation/activate", methods=["POST"])
def activate():
    data = request.get_json()
    gvlk_key = (data.get("gvlk_key") or "").strip()
    kms_server = (data.get("kms_server") or "").strip()

    if not gvlk_key:
        return jsonify({"success": False, "message": "请输入 GVLK 密钥"}), 400
    if not kms_server:
        return jsonify({"success": False, "message": "请输入 KMS 服务器地址"}), 400

    steps = []

    ok, out = _run_slmgr(f"/ipk {gvlk_key}")
    steps.append({"step": "安装产品密钥 (slmgr /ipk)", "success": ok, "output": out})
    if not ok:
        return jsonify({"success": False, "message": "安装密钥失败", "steps": steps})

    ok, out = _run_slmgr(f"/skms {kms_server}")
    steps.append({"step": "设置 KMS 服务器 (slmgr /skms)", "success": ok, "output": out})
    if not ok:
        return jsonify({"success": False, "message": "设置 KMS 服务器失败", "steps": steps})

    ok, out = _run_slmgr("/ato")
    steps.append({"step": "激活 Windows (slmgr /ato)", "success": ok, "output": out})

    ok_xpr, out_xpr = _run_slmgr("/xpr")
    steps.append({"step": "查询激活状态 (slmgr /xpr)", "success": ok_xpr, "output": out_xpr})

    all_ok = all(s["success"] for s in steps)
    return jsonify({
        "success": all_ok,
        "message": "Windows 激活完成" if all_ok else "激活过程中出现错误",
        "steps": steps,
    })
