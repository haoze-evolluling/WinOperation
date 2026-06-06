import re
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from services.shutdown_mgmt import (
    initiate_shutdown,
    abort_shutdown,
    create_scheduled_shutdown,
    list_scheduled_shutdowns,
    delete_scheduled_shutdown,
)

scheduler_bp = Blueprint("scheduler", __name__)

_shutdown_expires = None


@scheduler_bp.route("/api/shutdown/status", methods=["GET"])
def shutdown_status():
    global _shutdown_expires

    if _shutdown_expires is None:
        active = False
        remaining = None
    else:
        remaining = max(0, int(_shutdown_expires - time.time()))
        if remaining <= 0:
            _shutdown_expires = None
            active = False
            remaining = None
        else:
            active = True

    return jsonify({
        "success": True,
        "data": {
            "active": active,
            "remaining_seconds": remaining,
        },
    })


@scheduler_bp.route("/api/shutdown/timer", methods=["POST"])
def set_timer():
    global _shutdown_expires

    data = request.get_json()
    seconds = data.get("seconds")

    if seconds is None:
        time_str = data.get("time", "")
        m = re.match(r"^(\d{1,2}):(\d{2})$", time_str)
        if not m:
            return jsonify({"success": False, "message": "请提供 seconds 或有效的 time (HH:MM) 参数"}), 400
        now = datetime.now()
        target = now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0)
        if target <= now:
            target += timedelta(days=1)
        seconds = int((target - now).total_seconds())

    if seconds <= 0:
        return jsonify({"success": False, "message": "时间必须大于当前时间"}), 400

    abort_shutdown()
    ok, msg = initiate_shutdown(seconds)
    if not ok:
        return jsonify({"success": False, "message": msg}), 500

    _shutdown_expires = time.time() + seconds
    return jsonify({
        "success": True,
        "message": msg,
        "data": {"remaining_seconds": seconds},
    })


@scheduler_bp.route("/api/shutdown/cancel", methods=["POST"])
def cancel_shutdown():
    global _shutdown_expires

    ok, msg = abort_shutdown()
    if not ok:
        return jsonify({"success": False, "message": msg}), 500

    _shutdown_expires = None
    return jsonify({"success": True, "message": msg})


@scheduler_bp.route("/api/shutdown/schedule", methods=["POST"])
def create_schedule():
    data = request.get_json()
    days = data.get("days", [])
    time_str = data.get("time", "")

    if not days or not re.match(r"^\d{1,2}:\d{2}$", time_str):
        return jsonify({"success": False, "message": "请提供 days 列表和 time (HH:MM)"}), 400

    ok, msg = create_scheduled_shutdown(days, time_str)
    if not ok:
        return jsonify({"success": False, "message": msg}), 500
    return jsonify({"success": True, "message": msg})


@scheduler_bp.route("/api/shutdown/schedules", methods=["GET"])
def list_schedules():
    return jsonify({"success": True, "data": list_scheduled_shutdowns()})


@scheduler_bp.route("/api/shutdown/schedule/<int:schedule_id>", methods=["DELETE"])
def delete_schedule(schedule_id):
    schedules = list_scheduled_shutdowns()
    if 0 <= schedule_id < len(schedules):
        task_name = schedules[schedule_id].get("TaskName", "")
        ok, msg = delete_scheduled_shutdown(task_name)
        if not ok:
            return jsonify({"success": False, "message": msg}), 500
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "message": "未找到该计划"}), 404
