import os, requests
from datetime import datetime, timedelta
from flask import Blueprint, request, make_response, jsonify, redirect
from dotenv import load_dotenv
from config.db import User
from config.token import generate_token, verify_token
from config.hash import generate_hash, verify_hash

load_dotenv()

HOST = os.getenv("HOST", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

CLINET_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLINET_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = HOST + os.getenv("GOOGLE_REDIRECT_URI", "")

app = Blueprint("Authorization Routes", __name__, url_prefix='/auth')

@app.route("/")
def index():
    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "Authorization routes work perfectly"
    })


@app.route("/me", methods=['POST'])
def get_me():

    token = request.cookies.get('token') or ""
    if not token:
        return jsonify({
            "code": 200,
            "status": "OK",
            "authenticated": False,
            "message": 'Please signin. Token not found'
        })
    
    payload = verify_token(token)
    print(payload.keys())

    if "message" in payload.keys():
        return jsonify({
            "code": 200,
            "status": "OK",
            "authenticated": False,
            "message": "Please signin"
        })

    expiry = datetime.fromtimestamp(payload['exp'])
    current = datetime.now()

    print(expiry, current)

    if not expiry > current:
        return jsonify({
            "code": 200,
            "status": "OK",
            "authenticated": False,
            "message": "Token has been expired"
        })
    
    return jsonify({
        "code": 200,
        "status": "OK",
        "authenticated": True
    })


@app.route("/signin", methods=['POST'])
def signin():

    if request.content_type != "application/json":
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please provide details on json format"
        }), 403
    

    body = request.get_json()
    fields = [ 'email', 'password']
    available_fields = list(body.keys())


    for field in fields:
        if field not in available_fields:
            return jsonify({
                "code": 403,
                "status": "Forbidden",
                "message": f"Please provide detail of {field}"
            }), 403

    email = body['email'] or ''
    password = body['password'] or ''

    if not ( email or password ):
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Details should not be empty"
        }), 400

    users = []
    for user in User.stream():
        record = user.to_dict()
        record['id'] = user.id
        users.append(record)

    verified = False
    record = None

    for user in users:
        verified = verify_hash(password, user['password'])
        
        if verified:
            record = user
            break

    if not verified:
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Account does not exist"
        }), 400

    print(record)

    email = record['email']
    id = record['id']
    hash_password = record['password']

    token = generate_token(email, id)
    User.document(id).update({
        'token': token
    })

    # as response and jsonify creates different response
    # this combines them in one and send response in last
    response = make_response(jsonify({
        "code": 200,
        "status": "OK",
        "message": "Signed In successfully"
    }))

    response.set_cookie("token", token, 
        httponly=True,        
        samesite='Lax',       
        secure=False,         
        max_age=30*24*60*60
    )

    return response



@app.route("/user", methods=['POST'])
def create_user():
    if request.content_type != "application/json":
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please provide details on json format"
        }), 403
    
    body = request.get_json()
    fields = ['name', 'email', 'password']

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

    name = body['name'] or 0
    email = body['email'] or ''

    password = body['password'] or ''
    token = "token_in_process"

    if not ( name or email or password ):
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Details should not be empty"
        }), 400
    
    password = generate_hash(password)
    document = User.add({
        'name': name, 'email': email, 'password': password, 'token': token
    })

    id = document[1].id
    token = generate_token(email, id)
    
    User.document(id).update({
        'token': token
    })

    response = make_response(jsonify({
        "code": 200,
        "status": "OK",
        "message": "Account created successfully"
    }))

    response.set_cookie("token", token, 
        httponly=True,        
        samesite='Lax',       
        secure=False,         
        max_age=30*24*60*60
    )

    return response



@app.route("/google/callback")
def oauth_login():

    code = request.args.get("code")
    if not code:
        return redirect(f"{FRONTEND_URL}/failure")
    
    res = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code, "client_id": CLINET_ID, "client_secret": CLINET_SECRET,
        "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"
      })

    body = res.json()

    if res.status_code != 200:
        print(data)
        return redirect(f"{FRONTEND_URL}/failure")

    token = body['access_token']

    res = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    })
    data = res.json()

    print(data)

    name = data['name']
    email = data['email']

    document = User.add({
        'name': name, 'email': email, 'password': "not_necessary"
    })

    id = document[1].id
    token = generate_token(email, id)

    User.document(id).update({
        'token': token
    })

    response = redirect(f"{FRONTEND_URL}/success")
    response.set_cookie("token", token, 
        httponly=True,        
        samesite='Lax',       
        secure=False,         
        max_age=30*24*60*60
    )

    return response
