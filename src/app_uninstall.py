import subprocess
from flask import Blueprint, jsonify, request
from utils import CREATE_NO_WINDOW

app_uninstall_bp = Blueprint("app_uninstall", __name__)

APP_CATALOG = [
    {
        "title": "娱乐与社交类",
        "items": [
            {"label": "Xbox 全部组件", "icon": "🎮", "command": "Get-AppxPackage *xbox* | Remove-AppxPackage"},
            {"label": "Skype 客户端", "icon": "📹", "command": "Get-AppxPackage *skypeapp* | Remove-AppxPackage"},
            {"label": "纸牌游戏集合", "icon": "🃏", "command": "Get-AppxPackage *solitairecollection* | Remove-AppxPackage"},
            {"label": "您的手机", "icon": "📱", "command": "Get-AppxPackage *yourphone* | Remove-AppxPackage"},
            {"label": "人脉", "icon": "👥", "command": "Get-AppxPackage *people* | Remove-AppxPackage"},
        ],
    },
    {
        "title": "媒体与创作类",
        "items": [
            {"label": "电影和电视", "icon": "🎬", "command": "Get-AppxPackage *zunevideo* | Remove-AppxPackage"},
            {"label": "Groove 音乐", "icon": "🎧", "command": "Get-AppxPackage *zunemusic* | Remove-AppxPackage"},
            {"label": "3D 建模/打印相关", "icon": "🧊", "command": "Get-AppxPackage *3d* | Remove-AppxPackage"},
            {"label": "照片查看器", "icon": "🖼️", "command": "Get-AppxPackage *photos* | Remove-AppxPackage"},
            {"label": "混合现实门户", "icon": "🥽", "command": "Get-AppxPackage *mixedreality.portal* | Remove-AppxPackage"},
        ],
    },
    {
        "title": "新闻与工具类",
        "items": [
            {"label": "必应天气", "icon": "🌤️", "command": "Get-AppxPackage *bingweather* | Remove-AppxPackage"},
            {"label": "必应新闻", "icon": "📰", "command": "Get-AppxPackage *bingnews* | Remove-AppxPackage"},
            {"label": "Windows 地图", "icon": "🗺️", "command": "Get-AppxPackage *windowsmaps* | Remove-AppxPackage"},
            {"label": "OneNote (UWP版)", "icon": "📓", "command": "Get-AppxPackage *onenote* | Remove-AppxPackage"},
            {"label": "反馈中心", "icon": "💬", "command": "Get-AppxPackage *feedbackhub* | Remove-AppxPackage"},
            {"label": "邮件和日历", "icon": "📧", "command": "Get-AppxPackage *windowscommunicationsapps* | Remove-AppxPackage"},
            {"label": "计算器 (慎点)", "icon": "🧮", "command": "Get-AppxPackage *windowscalculator* | Remove-AppxPackage"},
        ],
    },
    {
        "title": "日常工具类",
        "items": [
            {"label": "闹钟和时钟", "icon": "⏰", "command": "Get-AppxPackage *windowsalarms* | Remove-AppxPackage"},
            {"label": "相机", "icon": "📷", "command": "Get-AppxPackage *windowscamera* | Remove-AppxPackage"},
            {"label": "录音机", "icon": "🎙️", "command": "Get-AppxPackage *soundrecorder* | Remove-AppxPackage"},
            {"label": "便签 (Sticky Notes)", "icon": "📝", "command": "Get-AppxPackage *stickynotes* | Remove-AppxPackage"},
            {"label": "截图和草图", "icon": "✂️", "command": "Get-AppxPackage *screensketch* | Remove-AppxPackage"},
        ],
    },
    {
        "title": "帮助与说明类",
        "items": [
            {"label": "提示 (Tips)", "icon": "💡", "command": "Get-AppxPackage *getstarted* | Remove-AppxPackage"},
            {"label": "获取帮助", "icon": "❓", "command": "Get-AppxPackage *gethelp* | Remove-AppxPackage"},
            {"label": "Office 助手", "icon": "📖", "command": "Get-AppxPackage *officehub* | Remove-AppxPackage"},
        ],
    },
    {
        "title": "媒体扩展与底层组件",
        "items": [
            {"label": "HEIF 图像扩展", "icon": "🖼️", "command": "Get-AppxPackage *heif* | Remove-AppxPackage"},
            {"label": "Web 媒体扩展", "icon": "🌐", "command": "Get-AppxPackage *webmedia* | Remove-AppxPackage"},
            {"label": "VP9 视频扩展", "icon": "🎥", "command": "Get-AppxPackage *vp9* | Remove-AppxPackage"},
        ],
    },
    {
        "title": "第三方推广与社交",
        "items": [
            {"label": "Spotify", "icon": "🎶", "command": "Get-AppxPackage *spotify* | Remove-AppxPackage"},
            {"label": "Disney+", "icon": "🏰", "command": "Get-AppxPackage *disney* | Remove-AppxPackage"},
            {"label": "消息 (Messaging)", "icon": "💬", "command": "Get-AppxPackage *messaging* | Remove-AppxPackage"},
        ],
    },
]


@app_uninstall_bp.route("/api/app-uninstall/catalog", methods=["GET"])
def app_catalog():
    item_count = sum(len(category["items"]) for category in APP_CATALOG)
    return jsonify({
        "success": True,
        "data": {
            "category_count": len(APP_CATALOG),
            "item_count": item_count,
            "categories": APP_CATALOG,
        },
    })


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
