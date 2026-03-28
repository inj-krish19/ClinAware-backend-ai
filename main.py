import joblib, os
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv

from app.automation import app as automation_blueprint
from app.routes.user import app as user_blueprint
from app.routes.auth import app as auth_blueprint

load_dotenv()
app = Flask(__name__)
encoder = LabelEncoder()

model = joblib.load('models/model.pkl')
regressor = joblib.load('models/regressor.pkl')

PORT = int( os.getenv("PORT", 12000) )


CORS(app)
app.register_blueprint(auth_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(automation_blueprint)

@app.route("/")
def root():
    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "App running well"
    })


@app.route("/predict", methods=['POST'])
def predict():

    if request.content_type != "application/json":
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please provide details of insurance"
        }), 403

    body = request.get_json()

    age = body['age'] or 0
    sex = body['sex'] or "not disclosed"
    bmi = body['bmi'] or 0

    region = body['region'] or "northeast"
    smoker = body['smoker'] or "smoker"
    children = body['children'] or 0

    if not (age or sex or bmi or region or smoker or children):
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Please provide all details"
        }), 400
    
    # if age <= 0 or bmi <= 0 or children < 0:
    #     return jsonify({
    #         "code": 400, 
    #         "status": "Bad Request",
    #         "message": "Age, BMI and Children count should not be negative"
    #     }), 400
    
    age = int(age)
    bmi = float(bmi)
    children = int(children)
    
    if sex not in ["male", "female"]:
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Sex should be me or female"
        }), 400
    
    if smoker not in ["yes", "no"]:
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Smoker selection should be from yes or no"
        }), 400

    if region not in ["northeast", "northwest", "southeast", "southwest"]:
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Region should be from north, south and east, west"
        }), 400

    sex = sex.lower()
    smoker = smoker.lower()
    region = region.lower()

    nn_model = joblib.load('models/nn.pkl')

    # sex = gender_map[sex]
    # smoker = smoker_map[smoker]
    # region = region_map[region]

    # print("Numericals", age, bmi, children)
    # print("Categorical", sex, smoker, region)

    # cost = model.predict(np.array([[age, sex, bmi, children, smoker, region]]) )

    # cost = np.array(cost).flatten()[0]
    # print("Cost", cost)

    input_df = pd.DataFrame([{
        "age": age, "bmi": bmi, "children": children, 
        "sex": sex, "smoker": smoker, "region": region
    }])
    print(input_df)

    cost_nn = nn_model.predict(input_df).flatten()[0]
    cost_model = model.predict(input_df).flatten()[0]
    cost_regressor = regressor.predict(input_df).flatten()[0]

    return jsonify({
        "code": 200,
        "status": "OK",
        "cost": {
            "nn": float(round(cost_nn // 12, -2)),
            "model": float(round(cost_model // 12, -2)),
            "regressor":  float(round(cost_regressor // 12, -2))
        },
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
