from flask import Blueprint, jsonify, request
from config.db import Insurance
from config.token import validate_token, verify_token

app = Blueprint("Insurance related route", __name__, url_prefix="/insurance")

@app.route("/")
def index():
    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "Insurance routes are working perfectly"
    })


@app.route("/history")
def history():
    
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please Sign In. Token not found"
        }), 403
    
    token = request.cookies.get("token")
    payload = verify_token(token)

    if "message" in payload.keys():
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Token expired"
        }), 403
    
    id = payload['id']
    history = Insurance.where("user", "==", id).stream()
    
    data = []
    for insurance_details in history:
        record = insurance_details.to_dict()
        # record['id'] = history[1]
        data.append(record)

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": data
    })
