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



# Chronic Condition and Non Chronic Condition Analysis for Average Premium
chroning_age_avg_premium = df.groupby(by=['smoker', 'age'])['charges'].sum()
chroning_age_avg_count = df.groupby(by=['smoker', 'age'])['charges'].count()

chronic_condition_data_charge = chroning_age_avg_premium['yes']
nonchronic_condition_data_charge = chroning_age_avg_premium['no']

chronic_condition_data_count = chroning_age_avg_count['yes']
nonchronic_condition_data_count = chroning_age_avg_count['no']


# SMOKER 
chronic_condition_stats = [
    { 'age': '18-25', 'min': 18, 'max': 25 },
    { 'age': '26-33', 'min': 26, 'max': 33 },
    { 'age': '34-40', 'min': 33, 'max': 40 },
    { 'age': '41-47', 'min': 41, 'max': 47 },
    { 'age': '48-55', 'min': 48, 'max': 55 },
    { 'age': '56-64', 'min': 56, 'max': 64 }
]

for record in chronic_condition_stats:

    count = 0
    charge = 0

    # Same for both categories
    min_age = record['min']
    max_age = record['max']

    for age in range(min_age, max_age+1):
        count += chronic_condition_data_count[age]
        charge += chronic_condition_data_charge[age]
    
    record['count'] = int(count)
    record['total'] = float(round(charge))

    record['yearly'] =  float(round(charge // count, -2))
    record['monthly'] = float(round(record['yearly'] // 12, -2))


@app.route("/chronic-age-avg-premium")
def chronic_condition_age_average_premium():
    return jsonify({
        "code": 200,
        "status": "OK",
        "data": chronic_condition_stats
    })


# NON SMOKER
nonchronic_condition_stats = [
    { 'age': '18-25', 'min': 18, 'max': 25 },
    { 'age': '26-33', 'min': 26, 'max': 33 },
    { 'age': '34-40', 'min': 33, 'max': 40 },
    { 'age': '41-47', 'min': 41, 'max': 47 },
    { 'age': '48-55', 'min': 48, 'max': 55 },
    { 'age': '56-64', 'min': 56, 'max': 64 }
]

for record in nonchronic_condition_stats:

    count = 0
    charge = 0

    # Same for both categories
    min_age = record['min']
    max_age = record['max']

    for age in range(min_age, max_age+1):
        count += nonchronic_condition_data_count[age]
        charge += nonchronic_condition_data_charge[age]

    record['count'] = int(count)
    record['total'] = float(round(charge))

    record['yearly'] =  float(round(charge // count, -2))
    record['monthly'] = float(round(record['yearly'] // 12, -2))


@app.route("/nonchronic-age-avg-premium")
def nonchronic_condition_age_average_premium():
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
chronic_condition_region_stats = []
chroning_region_avg_premium = df.groupby(by=['smoker', 'region'])['charges'].mean()

chronic_condition_premium = chroning_region_avg_premium['yes']
nonchronic_condition_premium = chroning_region_avg_premium['no']


for region in chronic_condition_premium.index:
    chronic_condition_region_stats.append({ 
        'region': region, 
        'yearly': round(chronic_condition_premium[region], -2),
        'monthly': round(chronic_condition_premium[region] // 12, -2)
    }) 

@app.route("/chronic-region-avg-premium")
def region_chronic_condition_average_premium():

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": chronic_condition_region_stats
    })



# Nonchronic_condition Region Average Premium
nonchronic_condition_region_stats = []
for region in nonchronic_condition_premium.index:
    nonchronic_condition_region_stats.append({
        'region': region,
        'yearly': round(nonchronic_condition_premium[region], -2),
        'monthly': round(nonchronic_condition_premium[region] // 12, -2)
    })

@app.route("/nonchronic-region-avg-premium")
def region_nonchronic_condition_average_premium():

    return jsonify({
        "code": 200,
        "status": "OK",
        "data": nonchronic_condition_region_stats
    })
