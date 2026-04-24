import os, requests
import io, json,  base64
from flask import Blueprint, request, jsonify
from config.db import Reports, User
from config.token import validate_token, verify_token
from datetime import datetime
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

app = Blueprint('report_ai', __name__, url_prefix='/report-ai')

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Medical Analysis System Instruction
SYSTEM_PROMPT = """
You are a Clinical Medical Report Assistant. Analyze the provided medical report (PDF or Image). 
1. Extract key biomarkers (e.g., HbA1c, Cholesterol, Glucose, Blood Pressure).
2. Simplify complex medical jargon into easy-to-understand patient language.
3. Provide a brief health summary and flag any "High" or "Low" anomalies.
4. IMPORTANT: Output your response ONLY in the following JSON format:
{
    "summary": "Short paragraph summary",
    "markers": [{"name": "Marker Name", "value": "Value", "status": "Normal/High/Low"}],
    "risk_index": "Low/Moderate/High"
}
"""

@app.route('/upload', methods=['POST'])
def process_medical_report():
    # 1. Auth Logic
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({"code": 403, "message": "Sign In Required"}), 403
    
    token = request.cookies.get("token")
    payload = verify_token(token)
    user_id = payload.get('id')

    # 2. File Check
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "No file"}), 400
    
    file = request.files['file']
    mime_type = file.content_type
    file_bytes = file.read()

    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        # Convert file to base64
        file_base64 = base64.b64encode(file_bytes).decode("utf-8")

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": file_base64
                            }
                        },
                        {
                            "text": "Extract structured clinical data from this document."
                        }
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": SYSTEM_PROMPT
                    }
                ]
            },
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }

        response = requests.post(
            f"{url}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )

        res_json = response.json()

        # Extract text (same as SDK's response.text)
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']

        # Convert to JSON
        analysis = json.loads(raw_text)

        # 5. Archive to Firestore
        report_record = {
            "user_id": user_id,
            "filename": file.filename,
            "analysis": analysis,
            "timestamp": datetime.now()
        }
        Reports.add(report_record)
        
        return jsonify({
            "code": 201,
            "status": "Success",
            "data": analysis
        }), 201

    except Exception as e:
        print(f"Report AI Error: {e}")
        return jsonify({"code": 500, "message": "Neural interpretation failed"}), 500

@app.route('/history', methods=['GET'])
def get_report_history():
    authenticated = validate_token(request)
    if not authenticated: return jsonify({"code": 403, "message": "Unauthorized"}), 403
    
    token = request.cookies.get("token")
    payload = verify_token(token)
    user_id = payload['id']
    
    try:
        docs = Reports.where("user_id", "==", user_id).stream()
        logs = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            if 'timestamp' in d: d['timestamp'] = d['timestamp'].isoformat()
            logs.append(d)
            
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify({"code": 200, "data": logs}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500