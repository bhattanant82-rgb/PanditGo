from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)  # Frontend se calls allow karta hai (localhost, Netlify, etc.)

# Gmail SMTP Setup
EMAIL_ADDRESS = "bhattanant82@gmail.com"
EMAIL_PASSWORD = "dfnm civm jmih uoqb"

def send_admin_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
        print(f"Email sent successfully: {subject}")
    except Exception as e:
        print(f"Email sending failed: {e}")

# Razorpay Real Keys (Live Mode)
RAZORPAY_KEY_ID = "rzp_live_RvnLDFb7F45oWy"
RAZORPAY_SECRET = "ZT3sVSgcQhSyR9yr36vJqn0I"

# Real Refund Endpoint
@app.route('/refund', methods=['POST'])
def refund():
    try:
        data = request.json
        payment_id = data.get('payment_id')
        amount = data.get('amount', 100)  # Default 1 ₹ = 100 paise

        if not payment_id:
            return jsonify({"success": False, "error": "Payment ID missing"}), 400

        url = f"https://api.razorpay.com/v1/payments/{payment_id}/refund"
        auth = HTTPBasicAuth(RAZORPAY_KEY_ID, RAZORPAY_SECRET)
        payload = {"amount": amount}

        response = requests.post(url, auth=auth, json=payload)
        refund_data = response.json()

        if response.status_code == 201:
            send_admin_email(
                "Refund Processed - ₹1 Advance",
                f"Refund of ₹{amount/100} processed.\n"
                f"Payment ID: {payment_id}\n"
                f"Refund ID: {refund_data.get('id')}\n"
                f"User refunded advance payment."
            )
            return jsonify({
                "success": True,
                "message": "Refund processed successfully",
                "refund_id": refund_data.get('id')
            })
        else:
            error_msg = refund_data.get('error', {}).get('description', 'Refund failed')
            return jsonify({"success": False, "error": error_msg}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ================= Kundli Generation (Vedic) =================

# ================= Kundli Generation (REAL – Prokerala) =================

PROKERALA_CLIENT_ID = "8ff2fde0-e9f6-41e5-ba80-adf7032f7a45 "
PROKERALA_CLIENT_SECRET = "ZrOfGGigsni5RpDsq3n1S3eH0LMIog29nAjRzAQI"

def get_prokerala_token():
    url = "https://api.prokerala.com/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": PROKERALA_CLIENT_ID,
        "client_secret": PROKERALA_CLIENT_SECRET
    }
    res = requests.post(url, data=payload)
    data = res.json()
    return data.get("access_token")


@app.route('/generate-kundli', methods=['POST'])
def generate_kundli():
    try:
        data = request.json

        dob = data.get('dob')    # YYYY-MM-DD
        tob = data.get('tob')    # HH:MM
        place = data.get('place')  # City name (future use)

        if not dob or not tob:
            return jsonify({"error": "DOB or TOB missing"}), 400

        # Temporary static coordinates (Ahmedabad)
        coordinates = "23.0225,72.5714"

        # ISO datetime (IST)
        datetime_str = f"{dob}T{tob}:00+05:30"

        token = get_prokerala_token()
        if not token:
            return jsonify({"error": "Failed to get Prokerala token"}), 500

        url = (
            "https://api.prokerala.com/v2/astrology/kundli"
            f"?datetime={datetime_str}"
            f"&coordinates={coordinates}"
            "&ayanamsa=1"
        )

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers)
        kundli_data = response.json()

        if kundli_data.get("status") != "ok":
            return jsonify({
                "error": "Kundli API error",
                "raw": kundli_data
            }), 400

        # Send ONLY useful data to frontend
        return jsonify({
            "status": "ok",
            "data": kundli_data.get("data")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/request-refund', methods=['POST'])
def request_refund():
    try:
        data = request.json
        booking_id = data.get('booking_id')
        reason = data.get('reason')
        amount = data.get('amount')

        print(f"Refund Request: Booking #{booking_id}, Reason: {reason}, Amount: ₹{amount}")

        subject = f"Refund Request - Booking #{booking_id}"
        body = f"""
        Refund request received!

        Booking ID: {booking_id}
        Reason: {reason}
        Amount: ₹{amount}

        Please review and approve/reject in dashboard.
        """
        send_admin_email(subject, body)

        return jsonify({"message": "Refund request submitted! Admin will review.", "success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/admin-dashboard', methods=['GET'])
def admin_dashboard():
    data = {
        "totalBookings": 45,
        "totalRevenue": 150000,
        "todaySales": 5000,
        "monthSales": 75000,
        "pendingPujas": 8,
        "activePandits": 42,
        "bookings": [
            {"id": 1, "user": "Rahul Sharma", "puja": "Griha Pravesh", "pandit": "Pt. Ram Sharma", "datetime": "01/01/2026 10:00", "amount": 2500, "status": "Pending"},
            {"id": 2, "user": "Priya Mehta", "puja": "Marriage Puja", "pandit": "Pt. Vikram Patel", "datetime": "05/01/2026 09:00", "amount": 3500, "status": "Confirmed"}
        ],
        "refunds": [
            {"bookingId": 3, "user": "Amit Patel", "amount": 1800, "reason": "Pandit not available", "status": "Pending"}
        ],
        "pendingPandits": [
            {"id": 1, "name": "Pt. Sanjay Mishra", "city": "Surat", "experience": "17 Years", "language": "Hindi", "status": "Pending"}
        ]
    }
    return jsonify(data)


@app.route('/admin-action', methods=['POST'])
def admin_action():
    data = request.json
    action = data['type']
    id = data['id']
    return jsonify({"message": f"{action} successful for ID {id}", "success": True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)