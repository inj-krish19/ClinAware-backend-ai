# ClinAware: Integrated Healthcare Intelligence Platform

**ClinAware** is an end-to-end medical assistance ecosystem that leverages Machine Learning (ML), Deep Learning (DL), and Web Automation to provide actionable health insights. The project bridges the gap between raw medical data and user-centric healthcare solutions.

---

## 🚀 Project Overview

The platform consists of three core modules designed to demonstrate a full range of data science capabilities: **Web Automation & NLP**, **Predictive Tabular Modeling**, and **Medical Computer Vision**.

### 🛠 Tech Stack

- **Frontend:** React.js, Vite.js
- **Backend:** Flask (Python)
- **Machine Learning:** Scikit-learn, Pandas, NumPy
- **Deep Learning:** TensorFlow, Keras, OpenCV
- **Data Visualization:** Matplotlib, Seaborn

---

## 📂 Module Breakdown

### 1. Automation: Global Health News Bot

- **Problem:** Medical professionals and students struggle to keep up with daily global healthcare trends.
- **Solution:** A web-scraping bot that aggregates the latest medical news, simplifies the headlines, and displays them on the ClinAware dashboard.
- **Tech:** Python, Extenral APIs.

### 2. ML: Medical Insurance Cost Predictor

- **Problem:** Patients often face "bill shock" due to unpredictable healthcare costs.
- **Solution:** A regression-based model that predicts annual insurance premiums based on age, BMI, smoking status, and region.
- **Algorithm:** Linear Regression / Random Forest Regressor.
- **Dataset:** [Kaggle - Medical Cost Personal Datasets](https://www.kaggle.com/datasets/mirichoi0218/insurance)

### 3. DL: Skin Cancer Multi-Class Classifier (Primary)

- **Problem:** Early detection of malignant skin lesions (like Melanoma) significantly increases survival rates, but specialist access is limited.
- **Solution:** A high-precision CNN that classifies skin lesions into 7 distinct diagnostic categories from user-uploaded images.
- **Algorithm:** CNN (MobileNetV2 Transfer Learning).
- **Dataset:** [Kaggle - HAM10000 Dataset](https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000)

> **Note:** This project also includes a secondary backup module for **Brain Tumor MRI Classification** (4 classes: Glioma, Meningioma, Pituitary, No Tumor) using the [Sartaj Dataset](https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri).

---

## 🏗 System Architecture

1.  **Data Ingestion:** User inputs data (Tabular for Insurance, Images for Skin Cancer).
2.  **Preprocessing:** Data is normalized, resized ($224 \times 224$ for images), and augmented to handle class imbalance.
3.  **Inference:** The Flask server loads the `.h5` (TensorFlow) or `.pkl` (Scikit-learn) models.
4.  **Visualization:** Results are displayed with confidence scores and interactive charts.

---

## 📈 Key Learning Objectives

- **Class Imbalance Management:** Using Oversampling and Image Augmentation for the HAM10000 dataset.
- **Transfer Learning:** Utilizing pre-trained weights to achieve high accuracy with smaller medical datasets.
- **Model Deployment:** Creating a REST API using Flask to serve Deep Learning models in real-time.
- **Statistics:** Applying probability theory to interpret model confidence intervals.

---

## 🔗 Resources & Data Sources

- **Skin Cancer Data:** [ISIC Archive / HAM10000](https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000)
- **Insurance Data:** [US Health Insurance Dataset](https://www.kaggle.com/datasets/mirichoi0218/insurance)
- **Frameworks:** [TensorFlow Documentation](https://www.tensorflow.org/), [Flask Documentation](https://flask.palletsprojects.com/)

---
