from flask import Blueprint, jsonify

from services.system_insights import get_insights_snapshot


insights_bp = Blueprint("insights", __name__)


@insights_bp.route("/api/insights/snapshot", methods=["GET"])
def insights_snapshot():
    return jsonify({"success": True, "data": get_insights_snapshot()})
