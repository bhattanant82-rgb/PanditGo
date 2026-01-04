from flask import Flask, request, jsonify
from flask_cors import CORS
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation, AltAz, get_sun
from astropy.coordinates import get_moon
import astropy.units as u
from datetime import datetime
import math
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
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Email failed: {e}")

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

RASHIS = ["Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)", "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)", "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
DASHA_EFFECTS = {"Ketu": "Spirituality, detachment, sudden changes", "Venus": "Luxury, marriage, creativity, wealth", "Sun": "Leadership, government, fame, health", "Moon": "Emotions, family, mind, mother", "Mars": "Energy, property, courage, conflicts", "Rahu": "Foreign, sudden gains/loss, obsession", "Jupiter": "Wisdom, education, finance, growth", "Saturn": "Hard work, delay, discipline, longevity", "Mercury": "Business, communication, intellect"}

def degree_to_rashi(deg):
    return RASHIS[int(deg // 30) % 12]

def degree_to_nakshatra(deg):
    return NAKSHATRAS[int(deg // (360/27)) % 27]

def get_lagna(birth_time, loc):
    frame = AltAz(obstime=birth_time, location=loc)
    sun = get_sun(birth_time)
    altaz = sun.transform_to(frame)
    lagna_deg = (altaz.az.degree - 24.0) % 360
    return lagna_deg

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

            moon_ra = get_moon(birth_time, loc).ra.degree
            rahu = (moon_ra + 180) % 360 - 24.0
            rahu = rahu % 360
            ketu = (rahu + 180) % 360
            positions['rahu'] = {"degree": round(rahu, 2), "rashi": degree_to_rashi(rahu), "nakshatra": degree_to_nakshatra(rahu)}
            positions['ketu'] = {"degree": round(ketu, 2), "rashi": degree_to_rashi(ketu), "nakshatra": degree_to_nakshatra(ketu)}

        lagna_deg = get_lagna(birth_time, loc)
        lagna = {
            "degree": round(lagna_deg, 2),
            "rashi": degree_to_rashi(lagna_deg),
            "nakshatra": degree_to_nakshatra(lagna_deg)
        }

        moon_deg = positions['moon']['degree']
        dasha_index = int(moon_deg // (360/27)) % 9
        dasha_lord = list(DASHA_EFFECTS.keys())[dasha_index]
        dasha = {
            "lord": dasha_lord,
            "effect": DASHA_EFFECTS[dasha_lord]
        }

        lagna_rashi = lagna['rashi']
        predictions = {
            "career": f"{lagna_rashi} Lagna mein strong leadership, management, tech ya govt jobs favorable.",
            "money": "Steady income. Investments long-term mein best. Speculation se bachna.",
            "marriage": "Shaadi mid-life mein strong. Partner supportive aur emotional.",
            "health": "Overall achhi health. Stress, digestion aur head pe dhyan rakhna."
        }

        return jsonify({
            "lagna": lagna,
            "graha": positions,
            "current_dasha": dasha,
            "predictions": predictions,
            "note": "Accurate Vedic Kundli with Lahiri Ayanamsa."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Baaki features same
@app.route('/become-pandit', methods=['POST'])
def become_pandit():
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        city = data.get('city')
        experience = data.get('experience')
        languages = data.get('languages')

        print(f"New Pandit: {name}, {phone}, {email}, {city}, {experience} years, {languages}")

        subject = "New Pandit Registration - Pending Approval"
        body = f"""
New pandit join request received!

Name: {name}
Phone: {phone}
Email: {email}
City: {city}
Experience: {experience} years
Languages: {languages}

Please review in admin dashboard.
        """
        send_admin_email(subject, body)

        return jsonify({"message": "Application submitted! Admin will review soon.", "success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ... baaki code same jaise refund, book-puja, request-refund, admin-dashboard

if __name__ == '__main__':
    app.run(debug=True, port=5000)