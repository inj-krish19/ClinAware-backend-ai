from flask import Blueprint, request, jsonify
from config.db import Vitals # Assuming Vitals is your Firestore Collection Reference
from config.token import validate_token, verify_token
from datetime import datetime

app = Blueprint('vitals', __name__, url_prefix='/vitals')

@app.route('/analyze', methods=['POST'])
def save_vitals():
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
    
    # 3. Process Data
    user_id = payload['id']
    data = request.json

    try:
        vital_record = {
            "user_id": user_id,
            "blood_pressure": {
                "systolic": data.get('systolic'),
                "diastolic": data.get('diastolic'),
                "status": data.get('bp_status') 
            },
            "diabetes": {
                "glucose": data.get('glucose'),
                "is_fasting": data.get('is_fasting'),
                "status": data.get('diabetes_status')
            },
            "timestamp": datetime.now() # Firestore handles Python datetime objects
        }
        
        # Firestore 'add' returns (time_ref, doc_ref)
        Vitals.add(vital_record)
        
        return jsonify({
            "code": 201,
            "status": "Success",
            "message": "Clinical metrics saved to Firestore"
        }), 201

    except Exception as e:
        print(f"Firestore Error: {e}")
        return jsonify({
            "code": 500,
            "status": "Error",
            "message": str(e)
        }), 500

@app.route('/history', methods=['GET'])
def get_vitals_history():
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({"code": 403, "message": "Unauthorized"}), 403
    
    token = request.cookies.get("token")
    payload = verify_token(token)
    
    if "message" in payload.keys():
        return jsonify({"code": 403, "message": "Invalid Session"}), 403

    user_id = payload['id']
    
    try:
        docs = Vitals.where("user_id", "==", user_id).stream()
        
        logs = []
        for doc in docs:
            log_data = doc.to_dict()
            log_data['id'] = doc.id
            if 'timestamp' in log_data:
                log_data['timestamp'] = log_data['timestamp'].isoformat()
            logs.append(log_data)
        
        # 2. Sort the list manually in Python
        # We sort by timestamp descending (newest first)
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        return jsonify({
            "code": 200,
            "data": logs
        }), 200
    except Exception as e:
        print(f"Firestore Query Error: {e}")
        return jsonify({"code": 500, "message": str(e)}), 500