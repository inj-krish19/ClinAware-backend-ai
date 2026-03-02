import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
encoder = LabelEncoder()

model = joblib.load('notebooks/model.pkl')
scaler = joblib.load('notebooks/scaler.pkl')
encoder = joblib.load('notebooks/encoder.pkl')


gender_map = {
    "female": 0,
    "male": 1
}

smoker_map = {
    "no": 0,
    "yes": 1
}

region_map = {
    "northeast": 0,
    "northwest": 1,
    "southeast": 2,
    "southwest": 3
}


@app.route("/")
def root():
    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "App running well"
    })


@app.route("/predict")
def predict():

    if request.content_type != "application/json":
        return jsonify({
            "code": 403,
            "status": "Forbidden",
            "message": "Please provide details of insurance"
        }), 403

    body = request.get_json()

    age = body['age']
    sex = body['sex']
    bmi = body['bmi']

    region = body['region']
    smoker = body['smoker']
    children = body['children']

    if not (age or sex or bmi or region or smoker or children):
        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "message": "Please provide all details"
        }), 400
    
    if age <= 0 or bmi <= 0 or children < 0:
        return jsonify({
            "code": 400, 
            "status": "Bad Request",
            "message": "Age, BMI and Children count should not be negative"
        }), 400
    
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

    # sex = gender_map[sex]
    # smoker = smoker_map[smoker]
    # region = region_map[region]

    # print("Numericals", age, bmi, children)
    # print("Categorical", sex, smoker, region)

    # cost = model.predict(np.array([[age, sex, bmi, children, smoker, region]]) )

    # cost = np.array(cost).flatten()[0]
    # print("Cost", cost)

    input_df = pd.DataFrame([body])
    cost = model.predict(input_df).flatten()[0]

    return jsonify({
        "code": 200,
        "status": "OK",
        "cost": cost
    })


if __name__ == "__main__":
    app.run(port=12000, debug=True)