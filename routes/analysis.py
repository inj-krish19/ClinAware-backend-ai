import numpy as np
import pandas as pd
from flask import Blueprint, jsonify

app = Blueprint("Analysis for Mediclaim related charts", __name__, url_prefix='/analysis')

df = pd.read_csv('notebooks/medical_insurance.csv')

@app.route("/")
def index():
    return jsonify({
        "code": 200,
        "status": "OK",
        "message": "Analysis route for analytical charts"
    })


# Analysis of Age and Premium 
age_avg_premium = df.groupby(by=['age'])['charges'].sum()
age_avg_count = df.groupby(by=['age'])['charges'].count()

data = {
    '18-25': { 'min': 18, 'max': 25, 'charge': 0 },
    '26-33': { 'min': 26, 'max': 33, 'charge': 0 },
    '34-40': { 'min': 33, 'max': 40, 'charge': 0 },
    '41-47': { 'min': 41, 'max': 47, 'charge': 0 },
    '48-55': { 'min': 48, 'max': 55, 'charge': 0 },
    '56-64': { 'min': 56, 'max': 64, 'charge': 0 }
}


for age_group in data.keys():

    count = 0
    charge = 0
    
    min_age = data[age_group]['min']
    max_age = data[age_group]['max']

    for age in range(min_age, max_age+1):
        count += age_avg_count[age]
        charge += age_avg_premium[age]
    
    data[age_group]['count'] = round(count, -2)
    data[age_group]['cumulative'] = round(charge, -2)
    data[age_group]['charge'] = round(charge // count, -2)

counts = [ d['count'] for d in list(data.values()) ]
yearly_premium = [ d['charge'] for d in list(data.values()) ]
monthly_premium = [ d['charge'] // 12 for d in list(data.values()) ]

age_groups = list(data.keys())

@app.route("/age-avg-premium-yearly")
def age_average_premium_yearly():

    return jsonify({
        "code": 200,
        "status": "OK",
        "age": age_groups,
        "premium": list(yearly_premium)
    })


@app.route("/age-avg-premium-monthly")
def age_average_premium_monthly():

    return jsonify({
        "code": 200,
        "status": "OK",
        "age": age_groups,
        "premium": list(monthly_premium)
    })
