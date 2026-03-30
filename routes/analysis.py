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


# Analysis of Age and Average Premium 
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



# Smoker and Nonsmoker Analysis for Average Premium
age_avg_premium = df.groupby(by=['smoker', 'age'])['charges'].sum()
age_avg_count = df.groupby(by=['smoker', 'age'])['charges'].count()

smoker_data_charge = age_avg_premium['yes']
nonsmoker_data_charge = age_avg_premium['no']

smoker_data_count = age_avg_count['yes']
nonsmoker_data_count = age_avg_count['no']

smoker_stats = {
    '18-25': { 'min': 18, 'max': 25, 'charge': 0 },
    '26-33': { 'min': 26, 'max': 33, 'charge': 0 },
    '34-40': { 'min': 33, 'max': 40, 'charge': 0 },
    '41-47': { 'min': 41, 'max': 47, 'charge': 0 },
    '48-55': { 'min': 48, 'max': 55, 'charge': 0 },
    '56-64': { 'min': 56, 'max': 64, 'charge': 0 }
}

nonsmoker_stats = {
    '18-25': { 'min': 18, 'max': 25, 'charge': 0 },
    '26-33': { 'min': 26, 'max': 33, 'charge': 0 },
    '34-40': { 'min': 33, 'max': 40, 'charge': 0 },
    '41-47': { 'min': 41, 'max': 47, 'charge': 0 },
    '48-55': { 'min': 48, 'max': 55, 'charge': 0 },
    '56-64': { 'min': 56, 'max': 64, 'charge': 0 }
}

for age_group in data.keys():

    # 0 for Smoker, 1 for Nonsmoker
    count = [0, 0]
    charge = [0, 0]

    # Same for both categories
    min_age = smoker_stats[age_group]['min']
    max_age = smoker_stats[age_group]['max']

    for age in range(min_age, max_age+1):
        count[0] += smoker_data_count[age]
        charge[0] += smoker_data_charge[age]

        count[1] += nonsmoker_data_count[age]
        charge[1] += nonsmoker_data_charge[age]
    
    smoker_stats[age_group]['count'] = round(count[0], -2)
    smoker_stats[age_group]['cumulative'] = round(charge[0], -2)
    smoker_stats[age_group]['charge'] = round(charge[0] // count[0], -2)

    nonsmoker_stats[age_group]['count'] = round(count[1], -2)
    nonsmoker_stats[age_group]['cumulative'] = round(charge[1], -2)
    nonsmoker_stats[age_group]['charge'] = round(charge[1] // count[1], -2)


# SMOKER 
smoker_counts = [ d['count'] for d in list(smoker_stats.values()) ]
smoker_yearly = [ d['charge'] for d in list(smoker_stats.values()) ]
smoker_monthly = [ d['charge'] // 12 for d in list(smoker_stats.values()) ]
smoker_age_groups = list(smoker_stats.keys())


@app.route("/smoker-age-avg-premium-yearly")
def smoker_age_average_premium_yearly():
    return jsonify({
        "code": 200,
        "status": "OK",
        "age": smoker_age_groups,
        "premium": list(smoker_yearly)
    })


@app.route("/smoker-age-avg-premium-monthly")
def smoker_age_average_premium_monthly():
    return jsonify({
        "code": 200,
        "status": "OK",
        "age": smoker_age_groups,
        "premium": list(smoker_monthly)
    })


# NON SMOKER 
nonsmoker_counts = [ d['count'] for d in list(nonsmoker_stats.values()) ]
nonsmoker_yearly = [ d['charge'] for d in list(nonsmoker_stats.values()) ]
nonsmoker_monthly = [ d['charge'] // 12 for d in list(nonsmoker_stats.values()) ]
nonsmoker_age_groups = list(smoker_stats.keys())


@app.route("/nonsmoker-age-avg-premium-yearly")
def nonsmoker_age_average_premium_yearly():
    return jsonify({
        "code": 200,
        "status": "OK",
        "age": nonsmoker_age_groups,
        "premium": list(nonsmoker_yearly)
    })


@app.route("/nonsmoker-age-avg-premium-monthly")
def nonsmoker_age_average_premium_monthly():
    return jsonify({
        "code": 200,
        "status": "OK",
        "age": nonsmoker_age_groups,
        "premium": list(nonsmoker_monthly)
    })


region_avg_premium = df.groupby(by=['region'])['charges'].mean()
region_age_groups = list(region_avg_premium.index)
region_premium = [ round(premium, -2) for premium in region_avg_premium.values ]

@app.route("/region-avg-premium")
def region_average_premium():

    return jsonify({
        "code": 200,
        "status": "OK",
        "age": region_age_groups,
        "premium": region_premium
    })


region_average_premium = df.groupby(by=['smoker', 'region'])['charges'].mean()

smoker_premium = region_average_premium['yes']
nonsmoker_premium = region_average_premium['no']

smoker_age_groups = list(smoker_premium.index)
smoker_avg_premium = [ round(premium, -2) for premium in smoker_premium.values ]

@app.route("/smoker-region-avg-premium")
def region_smoker_average_premium():

    return jsonify({
        "code": 200,
        "status": "OK",
        "age": smoker_age_groups,
        "premium": smoker_avg_premium
    })

nonsmoker_age_groups = list(nonsmoker_premium.index)
nonsmoker_avg_premium = [ round(premium, -2) for premium in nonsmoker_premium.values ]

@app.route("/nonsmoker-region-avg-premium")
def region_nonsmoker_average_premium():

    return jsonify({
        "code": 200,
        "status": "OK",
        "age": nonsmoker_age_groups,
        "premium": nonsmoker_avg_premium
    })
