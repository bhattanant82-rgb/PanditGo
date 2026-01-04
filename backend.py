from flask import Flask, request, jsonify
from flask_cors import CORS
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation, AltAz, get_sun
import astropy.units as u
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)

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
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Email failed: {e}")

RAZORPAY_KEY = "rzp_live_RvnLDFb7F45oWy"
RAZORPAY_SECRET = "ZT3sVSgcQhSyR9yr36vJqn0I"

@app.route('/refund', methods=['POST'])
def refund():
    try:
        data = request.json
        payment_id = data.get('payment_id')
        amount = data.get('amount', 100)
        if not payment_id:
            return jsonify({"success": False, "error": "Payment ID missing"}), 400
        url = f"https://api.razorpay.com/v1/payments/{payment_id}/refund"
        auth = HTTPBasicAuth(RAZORPAY_KEY, RAZORPAY_SECRET)
        payload = {"amount": amount}
        response = requests.post(url, auth=auth, json=payload)
        refund_data = response.json()
        if response.status_code == 201:
            send_admin_email("Refund Processed", f"₹{amount/100} refunded for {payment_id}")
            return jsonify({"success": True, "message": "Refund done"})
        else:
            return jsonify({"success": False, "error": "Refund failed"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

RASHIS = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

def degree_to_rashi(deg):
    return RASHIS[int(deg // 30) % 12]

def degree_to_nakshatra(deg):
    return NAKSHATRAS[int(deg // (360/27)) % 27]

@app.route('/generate-kundli', methods=['POST'])
def generate_kundli():
    try:
        data = request.json
        dob = data['dob']
        tob = data['tob']
        place = data['place']

        day, month, year = map(int, dob.split('/'))
        hour, minute = map(int, tob.split(':'))
        birth_dt = datetime(year, month, day, hour, minute, 0)
        birth_time = Time(birth_dt)

        lat, lon = map(float, place.split(','))
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=0*u.m)

        with solar_system_ephemeris.set('builtin'):
            planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']
            positions = {}
            for p in planets:
                body = get_body(p, birth_time, loc)
                ra = body.ra.degree
                sidereal = (ra - 24.0) % 360
                positions[p] = {
                    "degree": round(sidereal, 2),
                    "rashi": degree_to_rashi(sidereal),
                    "nakshatra": degree_to_nakshatra(sidereal)
                }

        # Simplified lagna (sun se approximate)
        sun_ra = get_body('sun', birth_time, loc).ra.degree
        lagna_deg = (sun_ra - 24.0) % 360
        lagna = {
            "degree": round(lagna_deg, 2),
            "rashi": degree_to_rashi(lagna_deg),
            "nakshatra": degree_to_nakshatra(lagna_deg)
        }

        moon_deg = positions['moon']['degree']
        dasha_index = int(moon_deg // (360/27)) % 9
        dasha_lord = list(DASHA_EFFECTS.keys())[dasha_index] # type: ignore
        dasha = {
            "lord": dasha_lord,
            "effect": "Positive influence in current period"
        }

        predictions = {
            "career": "Strong potential in leadership roles",
            "money": "Steady growth with smart planning",
            "marriage": "Harmonious relationship after mid-20s",
            "health": "Maintain balance, avoid stress"
        }

        return jsonify({
            "lagna": lagna,
            "graha": positions,
            "current_dasha": dasha,
            "predictions": predictions,
            "note": "Vedic Kundli generated with Lahiri Ayanamsa"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)