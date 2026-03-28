import jwt, os, datetime
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "notworking")

def generate_token(email, id):
    token = jwt.encode({
        "email": email, "id": str(id), 
        'exp': datetime.datetime.now() + datetime.timedelta(days=30)
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
    message = payload['message'] or ""

    if message in ["TOKEN_GENERATION_FAILED", ""]:
        return False

    expiry = payload['exp']
    if expiry > datetime.now():
        return False

    return True
