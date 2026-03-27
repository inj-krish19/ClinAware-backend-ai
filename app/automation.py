import os, requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify

load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "notfound")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "notfound")

CATEGORY = "business"
app = Blueprint(import_name=__name__, url_prefix='/automation', name="Automation News Bot")

@app.route("/")
def index():
    return jsonify({
        "code": 200,
        "message": "It works "
    })


@app.route("/news")
def get_news():

    index = 0

    response = requests.get(f'https://gnews.io/api/v4/top-headlines?category={CATEGORY}&apikey={GNEWS_API_KEY}&lang=en&county=us&max=10')
    data = response.json()

    print(data)

    return jsonify({
        "code": 200,
        "status": 'OK',
        "data": data
    })
