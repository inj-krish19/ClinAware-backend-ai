import os, requests
from flask import Blueprint, request, jsonify, redirect
from dotenv import load_dotenv

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
        "authorization": F"Bearer {token}"
    })
    data = res.json()

    print(data)

    return redirect(f"{FRONTEND_URL}/success")
