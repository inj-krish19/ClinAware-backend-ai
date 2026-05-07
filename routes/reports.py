from fpdf import FPDF
from datetime import datetime
import io, os, csv
import smtplib, base64, requests

from flask import Blueprint, jsonify, send_file, request
from email.message import EmailMessage
from google.cloud.firestore_v1.base_query import FieldFilter

# Firestore and Auth Imports
from config.db import User, Vitals, Reports, Insurance 
from config.token import validate_token, verify_token
from dotenv import load_dotenv

load_dotenv()
app = Blueprint("Report Generation", __name__, url_prefix='/report')

    

SMTP_SERVER = os.getenv("SMTP_SENDER")
SMTP_PORT = int(os.getenv("SMTP_PORT") or 0)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
MAIL_MICROSERVICE_URL = os.getenv("MAIL_MICROSERVICE_URL")



def calculate_age(dob_str):
    try:
        birth_date = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except:
        return "N/A"
    

def send_email_with_pdf(recipient_email, user_name, pdf_content):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Your ClinAware Comprehensive Report - {user_name}"
        msg["From"] = f"ClinAware Admin <{SENDER_EMAIL}>"
        msg["To"] = recipient_email

        msg.set_content(
            f"Hello {user_name},\n\n"
            f"Please find your requested clinical intelligence report attached.\n\n"
            f"Regards,\nClinAware Team"
        )

        msg.add_attachment(
            pdf_content,
            maintype="application",
            subtype="pdf",
            filename=f"ClinAware_{user_name}.pdf"
        )

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        return True

    except Exception as e:
        print(f"Email Protocol Error: {e}")
        return False
    

def generate_csv_data(user_id, vitals_query, insurance_query):
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 1. Vitals Section
    writer.writerow(["--- VITAL SIGNS HISTORY ---"])
    writer.writerow(["Date", "Systolic", "Diastolic", "BP Status", "Glucose", "Diabetes Status"])
    for doc in vitals_query:
        v = doc.to_dict()
        ts = v.get('timestamp').strftime('%Y-%m-%d') if v.get('timestamp') else "N/A"
        writer.writerow([
            ts, 
            v.get('blood_pressure', {}).get('systolic'),
            v.get('blood_pressure', {}).get('diastolic'),
            v.get('blood_pressure', {}).get('status'),
            v.get('diabetes', {}).get('glucose'),
            v.get('diabetes', {}).get('status')
        ])
    
    writer.writerow([]) # Spacer
    
    # 2. Insurance Section
    writer.writerow(["--- INSURANCE PREDICTIONS ---"])
    writer.writerow(["BMI", "Income", "Region", "Chronic Condition", "AI Premium (Alpha)", "AI Premium (Beta)"])
    for doc in insurance_query:
        ins = doc.to_dict()
        writer.writerow([
            ins.get('bmi'),
            ins.get('income'),
            ins.get('region'),
            ins.get('chronic_condition'),
            ins.get('predictions', {}).get('model'),
            ins.get('predictions', {}).get('regressor')
        ])
        
    return output.getvalue()




@app.route("/generate")
def generate_report():
    # 1. Authentication Handshake
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({"code": 403, "status": "Forbidden", "message": "Token not found"}), 403
    
    token = request.cookies.get("token")
    payload = verify_token(token)
    if "message" in payload.keys():
        return jsonify({"code": 403, "status": "Forbidden", "message": "Token expired"}), 403
    
    user_id = payload['id']
    
    # 2. Data Retrieval (No Limits)
    user_ref = User.document(user_id).get()
    if not user_ref.exists:
        return jsonify({"code": 404, "message": "User not found"}), 404
    user_record = user_ref.to_dict()

    # Chronic chronological sorting for Vitals and Reports
    vitals_query = Vitals.where("user_id", "==", user_id).order_by("timestamp", direction="DESCENDING").get()
    reports_query = Reports.where("user_id", "==", user_id).order_by("timestamp", direction="DESCENDING").get()
    
    # Unordered/Unsorted fetch for Insurance
    insurance_query = Insurance.where("user", "==", user_id).get()

    # 3. PDF Construction
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Branding Header
    pdf.set_fill_color(240, 248, 255) 
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "ClinAware Comprehensive Clinical Analysis", ln=True, align="C", fill=True)
    pdf.ln(5)

    # Section I: Demographics
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Patient Profile", ln=True)
    pdf.set_font("Helvetica", "", 10)
    age = calculate_age(user_record.get('dob', ''))
    dob = user_record.get('dob') or 'N/A'
    h, w = float(user_record.get('height', 0)), float(user_record.get('weight', 0))
    bmi = round(w / ((h/100)**2), 2) if h > 0 else "N/A"
    
    pdf.cell(0, 6, f"Name: {user_record.get('name')}", ln=True)
    pdf.cell(0, 6, f"Blood Group: {user_record.get('blood_group')}", ln=True)
    pdf.cell(0, 6, f"DOB: {dob} ", ln=True)
    pdf.cell(0, 6, f"Age: {age} | BMI: {bmi}", ln=True)
    pdf.cell(0, 6, f"Height: {h} | Weight : {w} ", ln=True)
    pdf.cell(0, 6, f"Email: {user_record.get('email')} ", ln=True)
    pdf.cell(0, 6, f"Clinical History: {user_record.get('chronic_condition')}", ln=True)
    pdf.ln(5)

    # Section II: Full Vitals History (Sorted)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Vital Signs Log ", ln=True)
    if vitals_query:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(40, 7, "Date", 1); pdf.cell(50, 7, "Blood Pressure", 1); pdf.cell(50, 7, "Glucose", 1); pdf.cell(50, 7, "Status", 1, ln=True)
        pdf.set_font("Helvetica", "", 9)
        for v_doc in vitals_query:
            v = v_doc.to_dict()
            bp = v.get('blood_pressure', {})
            dia = v.get('diabetes', {})
            ts = v.get('timestamp').strftime('%Y-%m-%d') if v.get('timestamp') else "N/A"
            pdf.cell(40, 7, ts, 1)
            pdf.cell(50, 7, f"{bp.get('systolic')}/{bp.get('diastolic')}", 1)
            pdf.cell(50, 7, f"{dia.get('glucose')} mg/dL", 1)
            pdf.cell(50, 7, bp.get('status'), 1, ln=True)
    pdf.ln(5)

    # Section III: Clinical Reports & AI Markers (Sorted)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Reports Intelligence (AI Vision)", ln=True)
    if reports_query:
        for r_doc in reports_query:
            r = r_doc.to_dict()
            pdf.set_font("Helvetica", "B", 10)
            analysis = r.get('analysis', {})
            risk_index = analysis['risk_index']
            summary = analysis['summary']
            markers = analysis['markers'] or []
            pdf.cell(0, 8, f"File: {r.get('filename', 'Unknown')} | Risk: {risk_index}", 1, ln=True, fill=True)
            pdf.set_font("Helvetica", "I", 9)
            pdf.multi_cell(0, 5, f"Summary: {summary}", border=1)
            
            # Dynamic Markers Loop
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_x(10)
            pdf.cell(80, 6, "Biomarker", 1); pdf.cell(55, 6, "Result", 1); pdf.cell(55, 6, "Status", 1, ln=True)
            pdf.set_font("Helvetica", "", 8)

            for marker in markers:
                pdf.cell(80, 6, str(marker.get('name', 'N/A')), 1)
                pdf.cell(55, 6, str(marker.get('value', 'N/A')), 1)
                
                # Optional: Color coding status text
                status = str(marker.get('status', 'N/A'))
                if status.lower() in ['high', 'abnormal', 'critical']:
                    pdf.set_text_color(200, 0, 0) # Red for alerts
                
                pdf.cell(55, 6, status, 1, ln=True)
                pdf.set_text_color(0, 0, 0) # Reset to black

            pdf.ln(4)
    pdf.ln(5)

    # Section IV: Insurance Predictions (No Sorting/No Limit)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "4. Insurance & Premium Forecasts", ln=True)
    if insurance_query:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(20, 7, "BMI", 1); 
        pdf.cell(40, 7, "Income", 1); 
        pdf.cell(45, 7, "Premium (AI)", 1); 
        pdf.cell(40, 7, "Region", 1)
        pdf.cell(45, 7, "Chronic", 1, ln=True)
        pdf.set_font("Helvetica", "", 9)

        for i_doc in insurance_query:
            ins = i_doc.to_dict()
            p = ins.get('predictions', {})
            pdf.cell(20, 7, str(ins.get('bmi')), 1)
            pdf.cell(40, 7, f"Rs. {ins.get('income', 0):,.2f}", 1)
            pdf.cell(45, 7, f"Rs. {p.get('regressor', 0):,.2f}", 1)
            pdf.cell(40, 7, ins.get('region', '').capitalize(), 1)
            pdf.cell(45, 7, ins.get('chronic_condition', '').capitalize(), 1, ln=True)

    # 4. Final Export
    output = io.BytesIO()
    pdf_content = pdf.output()
    output.write(pdf_content)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"ClinAware_{user_record.get('name')}.pdf"
    )



@app.route("/email")
def email_report():
    # 1. Authentication Handshake
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({"code": 403, "status": "Forbidden", "message": "Token not found"}), 403
    
    token = request.cookies.get("token")
    payload = verify_token(token)
    if "message" in payload.keys():
        return jsonify({"code": 403, "status": "Forbidden", "message": "Token expired"}), 403
    
    user_id = payload['id']
    
    # 2. Data Retrieval
    user_ref = User.document(user_id).get()
    if not user_ref.exists:
        return jsonify({"code": 404, "message": "User not found"}), 404
    user_record = user_ref.to_dict()
    user_email = user_record.get('email')

    if not user_email:
        return jsonify({"code": 400, "message": "User email not found in records"}), 400

    vitals_query = Vitals.where("user_id", "==", user_id).order_by("timestamp", direction="DESCENDING").get()
    reports_query = Reports.where("user_id", "==", user_id).order_by("timestamp", direction="DESCENDING").get()
    insurance_query = Insurance.where("user", "==", user_id).get()

    # 3. PDF Construction
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Branding Header
    pdf.set_fill_color(240, 248, 255) 
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "ClinAware Comprehensive Clinical Analysis", ln=True, align="C", fill=True)
    pdf.ln(5)

    # Section I: Demographics
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Patient Profile", ln=True)
    pdf.set_font("Helvetica", "", 10)
    age = calculate_age(user_record.get('dob', ''))
    dob = user_record.get('dob') or 'N/A'
    h, w = float(user_record.get('height', 0)), float(user_record.get('weight', 0))
    bmi = round(w / ((h/100)**2), 2) if h > 0 else "N/A"
    
    pdf.cell(0, 6, f"Name: {user_record.get('name')}", ln=True)
    pdf.cell(0, 6, f"Blood Group: {user_record.get('blood_group')}", ln=True)
    pdf.cell(0, 6, f"DOB: {dob} ", ln=True)
    pdf.cell(0, 6, f"Age: {age} | BMI: {bmi}", ln=True)
    pdf.cell(0, 6, f"Height: {h} | Weight : {w} ", ln=True)
    pdf.cell(0, 6, f"Email: {user_email} ", ln=True)
    pdf.cell(0, 6, f"Clinical History: {user_record.get('chronic_condition')}", ln=True)
    pdf.ln(5)

    # Section II: Full Vitals History
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Vital Signs Log", ln=True)
    if vitals_query:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(40, 7, "Date", 1); pdf.cell(50, 7, "Blood Pressure", 1); pdf.cell(50, 7, "Glucose", 1); pdf.cell(50, 7, "Status", 1, ln=True)
        pdf.set_font("Helvetica", "", 9)
        for v_doc in vitals_query:
            v = v_doc.to_dict()
            bp = v.get('blood_pressure', {})
            dia = v.get('diabetes', {})
            ts = v.get('timestamp').strftime('%Y-%m-%d') if v.get('timestamp') else "N/A"
            pdf.cell(40, 7, ts, 1)
            pdf.cell(50, 7, f"{bp.get('systolic')}/{bp.get('diastolic')}", 1)
            pdf.cell(50, 7, f"{dia.get('glucose')} mg/dL", 1)
            pdf.cell(50, 7, bp.get('status'), 1, ln=True)
    pdf.ln(5)

    # Section III: Clinical Reports & AI Markers
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Reports Intelligence (AI Vision)", ln=True)
    if reports_query:
        for r_doc in reports_query:
            r = r_doc.to_dict()
            pdf.set_font("Helvetica", "B", 10)
            analysis = r.get('analysis', {})
            risk_index = analysis.get('risk_index', 'N/A')
            summary = analysis.get('summary', 'No summary')
            markers = analysis.get('markers', [])
            
            pdf.cell(0, 8, f"File: {r.get('filename', 'Unknown')} | Risk: {risk_index}", 1, ln=True, fill=True)
            pdf.set_font("Helvetica", "I", 9)
            pdf.multi_cell(0, 5, f"Summary: {summary}", border=1)
            
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_x(10)
            pdf.cell(80, 6, "Biomarker", 1); pdf.cell(55, 6, "Result", 1); pdf.cell(55, 6, "Status", 1, ln=True)
            pdf.set_font("Helvetica", "", 8)

            for marker in markers:
                pdf.cell(80, 6, str(marker.get('name', 'N/A')), 1)
                pdf.cell(55, 6, str(marker.get('value', 'N/A')), 1)
                status = str(marker.get('status', 'N/A'))
                if status.lower() in ['high', 'abnormal', 'critical']:
                    pdf.set_text_color(200, 0, 0)
                pdf.cell(55, 6, status, 1, ln=True)
                pdf.set_text_color(0, 0, 0)
            pdf.ln(4)

    # Section IV: Insurance Predictions
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "4. Insurance & Premium Forecasts", ln=True)
    if insurance_query:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(20, 7, "BMI", 1); pdf.cell(40, 7, "Income", 1); pdf.cell(45, 7, "Premium (AI)", 1); pdf.cell(40, 7, "Region", 1); pdf.cell(45, 7, "Chronic", 1, ln=True)
        pdf.set_font("Helvetica", "", 9)

        for i_doc in insurance_query:
            ins = i_doc.to_dict()
            p = ins.get('predictions', {})
            pdf.cell(20, 7, str(ins.get('bmi')), 1)
            pdf.cell(40, 7, f"Rs. {ins.get('income', 0):,.2f}", 1)
            pdf.cell(45, 7, f"Rs. {p.get('regressor', 0):,.2f}", 1)
            pdf.cell(40, 7, ins.get('region', '').capitalize(), 1)
            pdf.cell(45, 7, ins.get('chronic_condition', '').capitalize(), 1, ln=True)

    # 4. Generate PDF Byte Stream
    pdf_output = pdf.output() 

    # 5. Prepare Data for Microservice
    # Convert raw bytes → base64 string
    pdf_b64 = base64.b64encode(pdf_output).decode("utf-8")

    payload = {
        "email": user_email,
        "filename": f"ClinAware_{user_record.get('name')}.pdf",
        "filedata": pdf_b64,
        "from": "ClinAware Admin",
    }

    try:
        # Note: I swapped the logic to return 200 ONLY if microservice returns 200
        resp = requests.post(f"{MAIL_MICROSERVICE_URL}/send", json=payload, timeout=10)

        print(resp.status_code)
        if resp.status_code == 200:
            return jsonify({
                "code": 200,
                "status": "Success",
                "message": f"Mail sent to {user_email}"
            }), 200
        else:
            return jsonify({
                "code": resp.status_code,
                "status": "Service Error",
                "message": "Mailing Microservice rejected the request."
            }), resp.status_code

    except requests.exceptions.RequestException as e:
        print(f"Microservice Connection Error: {e}")
        return jsonify({
            "code": 503,
            "status": "Relay Error",
            "message": "Unable to reach the Mailing Microservice."
        }), 503
    


@app.route("/download-csv")
def download_csv():
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({"code": 403, "status": "Forbidden", "message": "Token not found"}), 403
    
    token = request.cookies.get("token")

    payload = verify_token(token)
    if "message" in payload.keys():
        return jsonify({"code": 403, "status": "Forbidden", "message": "Token expired"}), 403
    user_id = payload['id']
    
    # Fetch Data
    vitals = Vitals.where(filter=FieldFilter("user_id", "==", user_id)).order_by("timestamp", direction="DESCENDING").get()
    insurance = Insurance.where(filter=FieldFilter("user", "==", user_id)).get()
    
    csv_content = generate_csv_data(user_id, vitals, insurance)
    
    return send_file(
        io.BytesIO(csv_content.encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"ClinAware_History_{user_id}.csv"
    )


@app.route("/mail-csv")
def mail_csv():
    authenticated = validate_token(request)
    if not authenticated:
        return jsonify({"code": 403, "status": "Forbidden", "message": "Token not found"}), 403
    
    token = request.cookies.get("token")

    payload = verify_token(token)
    if "message" in payload.keys():
        return jsonify({"code": 403, "status": "Forbidden", "message": "Token expired"}), 403
    user_id = payload['id']
    user_record = User.document(user_id).get().to_dict()
    user_email = user_record.get('email')

    # Fetch Data
    vitals = Vitals.where(filter=FieldFilter("user_id", "==", user_id)).order_by("timestamp", direction="DESCENDING").get()
    insurance = Insurance.where(filter=FieldFilter("user", "==", user_id)).get()
    
    # Generate and Encode
    csv_content = generate_csv_data(user_id, vitals, insurance)
    csv_b64 = base64.b64encode(csv_content.encode()).decode("utf-8")

    payload = {
        "email": user_email,
        "filename": f"ClinAware_Data_{user_record.get('name')}.csv",
        "filedata": csv_b64,
        "from": "ClinAware Admin",
    }

    try:
        resp = requests.post(f"{MAIL_MICROSERVICE_URL}/send", json=payload, timeout=10)
        if resp.status_code == 200:
            return jsonify({
                "code": 200,
                "status": "Success",
                "message": f"CSV History mailed to {user_email}"
            }), 200
        return jsonify({"code": 500, "message": "Microservice Error"}), 500
    except Exception as e:
        return jsonify({"code": 503, "message": str(e)}), 503