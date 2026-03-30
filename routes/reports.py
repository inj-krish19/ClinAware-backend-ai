from flask import Blueprint, jsonify

app = Blueprint("Report Generation", __name__, url_prefix='/report')

@app.route("/")
def index():
    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "Report generation route works perfectly"
    })
