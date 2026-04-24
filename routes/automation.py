import os, requests, base64
from dotenv import load_dotenv
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from config.db import Post

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

GEMINI_PROMPT = os.getenv("GEMINI_PROMPT", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "notfound")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "notfound")

LINKEDIN_TOKEN = os.getenv("LINKEDIN_TOKEN", "")
LINKEDIN_VERSION = os.getenv("LINKEDIN_VERSION", "")
LINKEDIN_ORGANIZATION_TOKEN = os.getenv("LINKEDIN_ORGANIZATION_TOKEN", "")


CATEGORY = "health"
app = Blueprint(import_name=__name__, url_prefix='/automation', name="Automation News Bot")


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

    response = requests.post("https://api.linkedin.com/rest/images?action=initializeUpload", headers=headers, json=body)
    res = response.json()
    
    return ( res['value']['uploadUrl'], res['value']['image'] )


def image_to_bytes(image_url):
    response = requests.get(image_url, stream=True)
    
    contentType = response.headers.get("Content-Type", "")
    if response.status_code != 200 or not contentType.startswith("image/"):
        print('Image Failed Returned Status', response.status_code)
        return 500, 'Failed'

    return 200, response.content


def upload_image(assestUrl, data):
    
    headers = {
        'Authorization': f'Bearer {LINKEDIN_TOKEN}',
        'Content-Type': 'application/octet-stream'
    }

    response = requests.put(assestUrl, headers=headers, data=data)
    return response

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

    response = requests.post('https://api.linkedin.com/rest/posts', headers=headers, json=body)
    print(response.json() if response.status_code != 201 else "Posted Successfully")

    return response.status_code, response.headers.get('x-restli-id')




@app.route("/")
def index():
    return jsonify({
        "code": 200,
        "message": "It works "
    })


@app.route("/api/news")
def provide_news():

    response = requests.get(f'https://gnews.io/api/v4/top-headlines?category={CATEGORY}&apikey={GNEWS_API_KEY}&lang=en&county=us&max=10')
    data = response.json()

    return jsonify({
        "code": 200,
        "status": 'OK',
        "data": data
    })

@app.route("/news", methods=['POST'])
def get_news():

    data = Post.stream()
    news = []

    for post in data:
        record = post.to_dict()
        record['id'] = post.id
        news.append(record)

    print(news)

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": news
    })    


@app.route("/post", methods=['GET', 'POST'])
def post_news():

    authorization = request.headers.get("authorization")

    if not authorization:
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Please provide the authorization header"
        })
    
    token = authorization[6:]
    verification_token = base64.b64encode(f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}".encode("utf-8")).decode("utf-8")
    print(token, verification_token)
    
    if (not token) or token != verification_token:
        return jsonify({
            "code": 401,
            "status": "Unauthorized",
            "message": "It requires special Admin access."
        }), 401

    index = int(request.args.get('index') or 0)
    bias = datetime.now().day % 3

    response = requests.get(f"https://gnews.io/api/v4/top-headlines?category={CATEGORY}&apikey={GNEWS_API_KEY}&lang=en&county=us&max=10")

    body = response.json()
    news_data = body['articles']
    
    news_index = index + bias
    news = news_data[news_index]
    print(news)


    # 1 - Register Image
    assest_url, assest_image = register_assest()

    # 2 - Fetch News and Image to Bytes
    status, image = image_to_bytes(news['image'])
    if status == 500:
        return jsonify({
            "code": 200,
            "status": "OK",
            "message": "News Posted Successfully"
        })

    # 3 - Generate Content
    json = {
        "contents": [{
            "parts": [{
                "text": f"{GEMINI_PROMPT} Description : {news['content']} and Article Link : {news['url']}"
            }]
        }]
    }
    response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}", json=json)
    body = response.json()

    content = body['candidates'][0]['content']['parts'][0]['text']


    # 4 - Upload Image or Assest
    response = upload_image(assest_url, image)
    if response.status_code != 201:
        return jsonify({
            'message': 'Image Publishing Failed'
        })
    else:
        message = f'Image Uploading Status : {status}'

    # 5 - Upload News on LinkedIn
    status, post_id = upload_post(news['title'], content, assest_image)

    if status == 400:
        message = 'Failed to Post'
    else:
        print(f'Status : {status} and ID : {post_id}')
        message = f'LinkedIn Organization Post Published Successfully {post_id}'


    # Saving in database
    document = Post.add({
        'title': news['title'],
        'content': news['content'],
        'description': content,
        'image': news['image'],
        'source': news['source']['name'] or "Not Disclosable Provider",
        'url': news['url'],
        'platform_url': f"https://www.linkedin.com/feed/update/{post_id}" or post_id
    })

    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "News Posted Successfully"
    })
