import firebase_admin, os
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT = os.getenv("SERVICE_ACCOUNT", "") 
PROJECT_ID = os.getenv("PROJECT_ID", "")
PRIVATE_KEY_ID = os.getenv("PRIVATE_KEY_ID", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL", "")
CLIENT_ID = os.getenv("CLIENT_ID", "")
AUTH_URI = os.getenv("AUTH_URI", "")
TOKEN_URI = os.getenv("TOKEN_URI", "")
AUTH_PROVIDER_CERTIFICATE_URL = os.getenv("AUTH_PROVIDER_CERTIFICATE_URL", "")
CLIENT_CERTIFICATE_URL = os.getenv("CLIENT_CERTIFICATE_URL", "")
UNIVERSAL_DOMAIN = os.getenv("UNIVERSAL_DOMAIN", "")


certificate = {
  "type": SERVICE_ACCOUNT,
  "project_id": PROJECT_ID,
  "private_key_id": PRIVATE_KEY_ID,
  "private_key": PRIVATE_KEY,
  "client_email": CLIENT_EMAIL,
  "client_id": CLIENT_ID,
  "auth_uri": AUTH_URI,
  "token_uri": TOKEN_URI,
  "auth_provider_x509_cert_url": AUTH_PROVIDER_CERTIFICATE_URL,
  "client_x509_cert_url": CLIENT_CERTIFICATE_URL,
  "universe_domain": UNIVERSAL_DOMAIN
}



cred = credentials.Certificate(certificate)
firebase_admin.initialize_app(cred)

db = firestore.client()
User = db.collection('users')
