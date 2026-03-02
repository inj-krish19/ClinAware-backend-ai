from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def root():
    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "App running well"
    })

if __name__ == "__main__":
    app.run(port=12000, debug=True)