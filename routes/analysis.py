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

data = [
    { 'age': '18-25', 'min': 18, 'max': 25 },
    { 'age': '26-33', 'min': 26, 'max': 33 },
    { 'age': '34-40', 'min': 33, 'max': 40 },
    { 'age': '41-47', 'min': 41, 'max': 47 },
    { 'age': '48-55', 'min': 48, 'max': 55 },
    { 'age': '56-64', 'min': 56, 'max': 64 }
]

for record in data:

    count = 0
    charge = 0
    
    min_age = record['min']
    max_age = record['max']

    for age in range(min_age, max_age+1):
        count += age_avg_count[age]
        charge += age_avg_premium[age]
    
    record['count'] = int(count)
    record['total'] = float(round(charge))

    record['yearly'] = float(round(charge // count, -2))
    record['monthly'] = float(round(record['yearly'] // 12, -2))


@app.route("/age-avg-premium")
def age_average_premium():
    return jsonify({
        "code": 200,
        "status": "OK",
        "data": data
    })



# Smoker and Nonsmoker Analysis for Average Premium
smoking_age_avg_premium = df.groupby(by=['smoker', 'age'])['charges'].sum()
smoking_age_avg_count = df.groupby(by=['smoker', 'age'])['charges'].count()

smoker_data_charge = smoking_age_avg_premium['yes']
nonsmoker_data_charge = smoking_age_avg_premium['no']

smoker_data_count = smoking_age_avg_count['yes']
nonsmoker_data_count = smoking_age_avg_count['no']


# SMOKER 
smoker_stats = [
    { 'age': '18-25', 'min': 18, 'max': 25 },
    { 'age': '26-33', 'min': 26, 'max': 33 },
    { 'age': '34-40', 'min': 33, 'max': 40 },
    { 'age': '41-47', 'min': 41, 'max': 47 },
    { 'age': '48-55', 'min': 48, 'max': 55 },
    { 'age': '56-64', 'min': 56, 'max': 64 }
]

for record in smoker_stats:

    count = 0
    charge = 0

    # Same for both categories
    min_age = record['min']
    max_age = record['max']

    for age in range(min_age, max_age+1):
        count += smoker_data_count[age]
        charge += smoker_data_charge[age]
    
    record['count'] = int(count)
    record['total'] = float(round(charge))

    record['yearly'] =  float(round(charge // count, -2))
    record['monthly'] = float(round(record['yearly'] // 12, -2))


@app.route("/smoker-age-avg-premium")
def smoker_age_average_premium():
    return jsonify({
        "code": 200,
        "status": "OK",
        "data": smoker_stats
    })


# NON SMOKER
nonsmoker_stats = [
    { 'age': '18-25', 'min': 18, 'max': 25 },
    { 'age': '26-33', 'min': 26, 'max': 33 },
    { 'age': '34-40', 'min': 33, 'max': 40 },
    { 'age': '41-47', 'min': 41, 'max': 47 },
    { 'age': '48-55', 'min': 48, 'max': 55 },
    { 'age': '56-64', 'min': 56, 'max': 64 }
]

for record in nonsmoker_stats:

    count = 0
    charge = 0

    # Same for both categories
    min_age = record['min']
    max_age = record['max']

    for age in range(min_age, max_age+1):
        count += nonsmoker_data_count[age]
        charge += nonsmoker_data_charge[age]

    record['count'] = int(count)
    record['total'] = float(round(charge))

    record['yearly'] =  float(round(charge // count, -2))
    record['monthly'] = float(round(record['yearly'] // 12, -2))


@app.route("/nonsmoker-age-avg-premium")
def nonsmoker_age_average_premium():
    return jsonify({
        "code": 200,
        "status": "OK",
        "data": data
    })



# Region and Average Premium 
region_avg_premium = df.groupby(by=['region'])['charges'].mean()
region_stats = []

for region in region_avg_premium.index:
    region_stats.append({ 
        'region': region, 
        'yearly': round(region_avg_premium[region], -2),
        'monthly': round(region_avg_premium[region] // 12, -2),
    })
    

@app.route("/region-avg-premium")
def region_average_premium():
    return jsonify({
        "code": 200,
        "status": "OK",
        "data": region_stats
    })



# Smoker Region Average Premium
smoker_region_stats = []
smoking_region_avg_premium = df.groupby(by=['smoker', 'region'])['charges'].mean()

smoker_premium = smoking_region_avg_premium['yes']
nonsmoker_premium = smoking_region_avg_premium['no']


for region in smoker_premium.index:
    smoker_region_stats.append({ 
        'region': region, 
        'yearly': round(smoker_premium[region], -2),
        'monthly': round(smoker_premium[region] // 12, -2)
    }) 

@app.route("/smoker-region-avg-premium")
def region_smoker_average_premium():

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": smoker_region_stats
    })



# Nonsmoker Region Average Premium
nonsmoker_region_stats = []
for region in nonsmoker_premium.index:
    nonsmoker_region_stats.append({
        'region': region,
        'yearly': round(nonsmoker_premium[region], -2),
        'monthly': round(nonsmoker_premium[region] // 12, -2)
    })

@app.route("/nonsmoker-region-avg-premium")
def region_nonsmoker_average_premium():

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": nonsmoker_region_stats
    })
