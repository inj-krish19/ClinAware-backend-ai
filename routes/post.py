from flask import Blueprint, jsonify, request
from config.db import Post

app = Blueprint("Post routes", __name__, url_prefix='/post')

@app.route("/")
def get_news():

    data = []
    records = Post.stream()

    for record in records:
        news = record.to_dict()
        news['id'] = record.id
        data.append(news)

    data.sort(key=lambda x: x['id'], reverse=True)
    return jsonify({
        "code": 200,
        "status": "OK",
        "data": data
    })
