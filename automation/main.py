import os, requests, base64
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Database Preparation
SERVICE_ACCOUNT = os.getenv("SERVICE_ACCOUNT", "") 
PROJECT_ID = os.getenv("PROJECT_ID", "")
PRIVATE_KEY_ID = os.getenv("PRIVATE_KEY_ID", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "").replace("\\n", "\n")
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
Post = db.collection('post')

app = FastAPI()

PORT = int(os.getenv("PORT", "") or 12000)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

GEMINI_PROMPT = os.getenv("GEMINI_PROMPT", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "notfound")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "notfound")

LINKEDIN_TOKEN = os.getenv("LINKEDIN_TOKEN", "")
LINKEDIN_VERSION = os.getenv("LINKEDIN_VERSION", "")
LINKEDIN_ORGANIZATION_TOKEN = os.getenv("LINKEDIN_ORGANIZATION_TOKEN", "")

CATEGORY = "health"


# -------------------- Helpers --------------------

def register_assest():
    headers = {
        'Authorization': f'Bearer {LINKEDIN_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': f'{LINKEDIN_VERSION}'
    }

    body = {
        'initializeUploadRequest': {
            'owner': f'urn:li:organization:{LINKEDIN_ORGANIZATION_TOKEN}'
        }
    }

    response = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=headers, json=body
    )

    res = response.json()
    return (res['value']['uploadUrl'], res['value']['image'])


def image_to_bytes(image_url):
    response = requests.get(image_url, stream=True)

    contentType = response.headers.get("Content-Type", "")
    if response.status_code != 200 or not contentType.startswith("image/"):
        return 500, 'Failed'

    return 200, response.content


def upload_image(assestUrl, data):
    headers = {
        'Authorization': f'Bearer {LINKEDIN_TOKEN}',
        'Content-Type': 'application/octet-stream'
    }

    return requests.put(assestUrl, headers=headers, data=data)


def upload_post(title, content, assestID):
    headers = {
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': f'{LINKEDIN_VERSION}',
        'Authorization': f'Bearer {LINKEDIN_TOKEN}'
    }

    organizationId = f'urn:li:organization:{LINKEDIN_ORGANIZATION_TOKEN}'

    body = {
        'author': organizationId,
        'commentary': content,
        'visibility': 'PUBLIC',
        'distribution': {
            'feedDistribution': 'MAIN_FEED',
            'targetEntities': [],
            'thirdPartyDistributionChannels': []
        },
        'content': {
            'media': {
                'title': title,
                'id': assestID
            }
        },
        'lifecycleState': 'PUBLISHED',
        'isReshareDisabledByAuthor': False
    }

    response = requests.post(
        'https://api.linkedin.com/rest/posts',
        headers=headers,
        json=body
    )

    return response.status_code, response.headers.get('x-restli-id')


# -------------------- Routes --------------------

@app.get("/")
def get_all_news():
    data = []

    for record in Post.stream():
        news = record.to_dict()
        news['id'] = record.id
        data.append(news)

    return {
        "code": 200,
        "status": "OK",
        "data": data
    }


@app.get("/api/news")
def provide_news():
    response = requests.get(
        f'https://gnews.io/api/v4/top-headlines?category={CATEGORY}&apikey={GNEWS_API_KEY}&lang=en&county=us&max=10'
    )

    return {
        "code": 200,
        "status": "OK",
        "data": response.json()
    }


@app.post("/news")
def get_news():
    news = []

    for post in Post.stream():
        record = post.to_dict()
        record['id'] = post.id
        news.append(record)

    return {
        "code": 200,
        "status": "OK",
        "data": news
    }


@app.get("/post")
@app.post("/post")
def post_news(request: Request):

    authorization = request.headers.get("authorization")

    if not authorization:
        raise HTTPException(status_code=400, detail="Missing authorization header")

    token = authorization[6:]
    verification_token = base64.b64encode(
        f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}".encode()
    ).decode()

    if token != verification_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    print("Verified")
    index = int(request.query_params.get('index', 0))
    bias = datetime.now().day % 3

    response = requests.get(
        f"https://gnews.io/api/v4/top-headlines?category={CATEGORY}&apikey={GNEWS_API_KEY}&lang=en&county=us&max=10"
    )

    news_data = response.json()['articles']
    news = news_data[index + bias]
    print(news)

    # 1
    assest_url, assest_image = register_assest()

    # 2
    status, image = image_to_bytes(news['image'])
    if status == 500:
        return {"message": "News Posted Successfully"}

    # 3
    gemini_res = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}",
        json={
            "contents": [{
                "parts": [{
                    "text": f"{GEMINI_PROMPT} Description : {news['content']} and Article Link : {news['url']}"
                }]
            }]
        }
    )

    content = gemini_res.json()['candidates'][0]['content']['parts'][0]['text']
    print(content)

    # 4
    response = upload_image(assest_url, image)
    if response.status_code != 201:
        return {'message': 'Image Publishing Failed'}

    # 5
    status, post_id = upload_post(news['title'], content, assest_image)
    print(status, post_id)

    # 6 DB
    Post.add({
        'title': news['title'],
        'content': news['content'],
        'description': content,
        'image': news['image'],
        'source': news['source']['name'] or "Not Disclosable Provider",
        'url': news['url'],
        'platform_url': f"https://www.linkedin.com/feed/update/{post_id}" or post_id
    })

    return {
        "code": 200,
        "status": "OK",
        "message": "News Posted Successfully"
    }