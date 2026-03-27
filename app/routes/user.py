from flask import Blueprint, jsonify, request
from config.db import User

app = Blueprint("User Routes", __name__, url_prefix='/user')


@app.route("/", methods=['GET'])
def get_all():
    users = User.stream()
    data = [ ]


    for user in users:
        record = user.to_dict()
        record['id'] = user.id
        data.append(record)

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": data
    }), 200


@app.route("/", methods=['POST'])
def create_user():
    if request.content_type != "application/json":
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please provide details on json format"
        }), 403
    
    body = request.get_json()
    fields = ['age', 'name', 'email', 'country', 'gender']

    available_fields = list(body.keys())

    print(fields)
    print(available_fields)

    for field in fields:
        if field not in available_fields:
            return jsonify({
                "code": 403,
                "status": "Forbidden",
                "message": f"Please provide detail of {field}"
            }), 403

    age = body['age'] or 0
    name = body['name'] or 0

    email = body['email'] or ''
    country = body['country'] or ''

    gender = body['gender'] or ''
    token = "token_in_process"

    if not ( age or name or email or gender or country  ):
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Details should not be empty"
        }), 400
    
    User.add({
        'age': age, 'name': name, 'email': email,
        'country': country, 'gender': gender, 'token': token
    })

    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "User created successfully"
    })
