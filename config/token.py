import jwt, os, datetime
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "notworking")

def get_token(email, id):
    token = jwt.encode({
        "email": email, "id": id, 
        'eat': datetime.datetime.now() + datetime.timedelta(days=30)
    }, SECRET_KEY, "HS256")

    return token

def get_payload(token):
    payload = jwt.decode(token, SECRET_KEY, "HS256")
    return token


def validate_token(token):

    return True
