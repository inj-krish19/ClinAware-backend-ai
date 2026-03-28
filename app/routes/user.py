from flask import Blueprint, jsonify
from config.db import User

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


