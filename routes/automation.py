import os, requests, base64
from dotenv import load_dotenv
from datetime import datetime
from flask import Blueprint, request, jsonify, make_response
from config.db import Post

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "notfound")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "notfound")

CATEGORY = "health"
app = Blueprint(import_name=__name__, url_prefix='/automation', name="Automation News Bot")

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

    document = Post.add({
        'title': news['title'],
        'content': news['content'],
        'image': news['image'],
        'source': news['source']['name'] or "Not Disclosable Provider",
        'url': news['url'],
    })

    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "News Posted Successfully"
    })
