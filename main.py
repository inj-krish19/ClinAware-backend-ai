import joblib, os
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv

from routes.auth import app as auth_blueprint
from routes.user import app as user_blueprint
from routes.post import app as post_blueprint
from routes.reports import app as report_blueprint
from routes.analysis import app as analysis_blueprint
from routes.insurance import app as insurance_blueprint
from routes.automation import app as automation_blueprint
from config.token import validate_token, verify_token
from config.db import Insurance

load_dotenv()
app = Flask(__name__)
encoder = LabelEncoder()

model = joblib.load('models/model.pkl')
regressor = joblib.load('models/regressor.pkl')

PORT = int( os.getenv("PORT", 12000) )
FRONTEND_URL = os.getenv("FRONTEND_URL", "")


CORS(app, origins=[FRONTEND_URL], supports_credentials=True)
app.register_blueprint(auth_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(post_blueprint)
app.register_blueprint(report_blueprint)
app.register_blueprint(analysis_blueprint)
app.register_blueprint(insurance_blueprint)
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

    authenticated = validate_token(request)
    if not authenticated: 
        print("Auth Fail")
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please Sign In"
        }), 403
    
    token = request.cookies.get("token") or ""
    payload = verify_token(token)

    if "message" in payload.keys():
        print("Keys fail")
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please Sign In. Token not found"
        }), 403

    id = payload['id']

    if request.content_type != "application/json":
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please provide details of insurance"
        }), 403

    body = request.get_json()
    name = body['name'] or ""
    income = body['income'] or 0

    age = body['age'] or 0
    sex = body['sex'] or "not disclosed"
    bmi = body['bmi'] or 0

    region = body['region'] or "northeast"
    chronic_condition = body['chronic_condition'] or "chronic_condition"
    children = body['children'] or 0

    if not (age or sex or bmi or region or chronic_condition or children or name or income):
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
    income = float(income)
    children = int(children)
    
    if sex not in ["male", "female"]:
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Sex should be me or female"
        }), 400
    
    if chronic_condition not in ["yes", "no"]:
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Chronic selection should be from yes or no. Please reheld it"
        }), 400

    if region not in ["northeast", "northwest", "southeast", "southwest"]:
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Region should be from north, south and east, west"
        }), 400

    sex = sex.lower()
    chronic_condition = chronic_condition.lower()
    region = region.lower()

    # nn_model = joblib.load('models/nn.pkl')

    # sex = gender_map[sex]
    # chronic_condition = chronic_condition_map[chronic_condition]
    # region = region_map[region]

    # print("Numericals", age, bmi, children)
    # print("Categorical", sex, chronic_condition, region)

    # cost = model.predict(np.array([[age, sex, bmi, children, chronic_condition, region]]) )

    # cost = np.array(cost).flatten()[0]
    # print("Cost", cost)

    input_df = pd.DataFrame([{
        "user": id, "name": name, 
        "age": age, "bmi": bmi, "children": children, 
        "sex": sex, "smoker": chronic_condition, "region": region
    }])
    print(input_df)

    # cost_nn = nn_model.predict(input_df).flatten()[0]
    cost_model = model.predict(input_df).flatten()[0]
    cost_regressor = regressor.predict(input_df).flatten()[0]

    Insurance.add({
        "age": age, "bmi": bmi, "children": children, 
        "sex": sex, "chronic_condition": chronic_condition, "region": region,
        "user": id, "name": name, "income": income, "predictions": {
            # "nn": float(round(cost_nn // 12, -2)),
            "model": float(round(cost_model // 12, -2)),
            "regressor":  float(round(cost_regressor // 12, -2))
        }
    })

    return jsonify({
        "code": 200,
        "status": "OK",
        "cost": {
            # "nn": float(round(cost_nn // 12, -2)),
            "model": float(round(cost_model // 12, -2)),
            "regressor":  float(round(cost_regressor // 12, -2))
        },
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
