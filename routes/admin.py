from flask import Blueprint, request, jsonify
from config.db import User, Insurance, Vitals, Reports, Post
import os

app = Blueprint('admin', __name__, url_prefix='/admin')

# The "Hardcoded" Secret
ADMIN_SECRET = "CLINAWARE_ADMIN"

def check_secret():
    # Looks for the key in the request headers
    return request.headers.get("X-Admin-Secret") == ADMIN_SECRET

@app.route('/stats', methods=['GET'])
def get_global_stats():
    if not check_secret():
        return jsonify({"code": 401, "message": "Unauthorized Nexus Access"}), 401

    # Aggregating all data for the "God View"
    users = User.stream()
    data = []

    for user in users:
        record = user.to_dict()
        record['id'] = user.id
        data.append(record)
    
    # We use .get() here to avoid long-running stream counts if the DB is big
    return jsonify({
        "code": 200,
        "total_users": len(data),
        "total_insurance": len([d for d in Insurance.stream()]),
        "total_vitals": len([d for d in Vitals.stream()]),
        "total_reports": len([d for d in Reports.stream()]),
        "users": data
    })

@app.route('/user-deep-dive/<uid>', methods=['GET'])
def get_user_full_history(uid):
    if not check_secret():
        return jsonify({"code": 401, "message": "Unauthorized"}), 401

    print(uid)
    # Collect everything related to this specific UID
    insurance = [d.to_dict() for d in Insurance.where("user", "==", uid).stream()]
    vitals = [d.to_dict() for d in Vitals.where("user_id", "==", uid).stream()]
    reports = [d.to_dict() for d in Reports.where("user_id", "==", uid).stream()]
    
    return jsonify({
        "code": 200,
        "data": {
            "insurance": insurance,
            "vitals": vitals,
            "reports": reports
        }
    })