from flask import Blueprint, jsonify, request
from config.db import User
from config.token import validate_token, verify_token

app = Blueprint("User Routes", __name__, url_prefix='/user')


@app.route("/", methods=['GET'])
def get_all():
    users = User.stream()
    data = []


    for user in users:
        record = user.to_dict()
        record['id'] = user.id
        data.append(record)

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": data
    }), 200


@app.route("/profile", methods=['GET'])
def get_profile():
    # 1. Authenticate Request
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please Sign In. Token not found"
        }), 403
    
    # 2. Extract and Verify Token
    token = request.cookies.get("token")
    payload = verify_token(token)

    if "message" in payload.keys():
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Token expired or invalid"
        }), 403
    
    # 3. Fetch User Data from DB
    user_id = payload['id']
    user_ref = User.document(user_id).get()

    if not user_ref.exists:
        return jsonify({
            "code": 404,
            "status": "Not Found",
            "message": "User clinical profile does not exist"
        }), 404

    data = user_ref.to_dict()
    data['id'] = user_ref.id # Ensure ID is included for frontend reference

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": data
    }), 200


@app.route("/update", methods=['PATCH'])
def update_profile():
    # 1. Authenticate Request
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Authentication required"
        }), 403
    
    token = request.cookies.get("token")
    payload = verify_token(token)

    if "message" in payload.keys():
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Session expired"
        }), 403

    try:
        user_id = payload['id']
        update_data = request.json
        
        # 2. Filter payload to prevent unauthorized field modification
        # Don't let users change their email or ID via this route
        protected_fields = ['id', 'email', 'created_at', 'role']
        sanitized_payload = {k: v for k, v in update_data.items() if k not in protected_fields}
        
        # 3. Update DB
        User.document(user_id).update(sanitized_payload)
        
        return jsonify({
            "code": 200,
            "status": "Success",
            "message": "Clinical profile synchronized successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "code": 500,
            "status": "Internal Server Error",
            "message": str(e)
        }), 500

@app.route("/all", methods=['GET'])
def get_all_users():
    """Admin route to see all users - ensure you add admin check here later"""
    # Simple check for now, you can refine this with payload['role']
    users = User.stream()
    data = []

    for user in users:
        record = user.to_dict()
        record['id'] = user.id
        data.append(record)

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": data
    }), 200