import jwt, os
from datetime import datetime, timedelta
from config.db import User
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "notworking")

def generate_token(email, id):
    token = jwt.encode({
        "email": email, "id": str(id), 
        'exp': datetime.now() + timedelta(days=30)
    }, SECRET_KEY, "HS256")

    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, "HS256")
        return payload
    except :
        return { "message": "TOKEN_GENERATION_FAILED" }


def validate_token(request):

    token = request.cookies.get('token') or ""
    if not token:
        return False
    
    payload = verify_token(token)
    if "message" in payload.keys():
        return False

    expiry = datetime.fromtimestamp(payload['exp'])

    if not expiry > datetime.now():
        return False
    
    id = payload['id']
    user = User.document(id).get()

    if user.exists:
        print("Document found!")
        print("Data:", user.to_dict())
        user = user.to_dict()
    else:
        print("Document does not exist")
        return False


    if token != user['token']:
        return False

    return True
