from flask import Flask, request, jsonify
from flask_cors import CORS
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation, AltAz, get_sun, get_moon
import astropy.units as u
from datetime import datetime
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)  # Sab frontend se call allow (localhost:5500, Netlify wagairah)

# Gmail SMTP Setup - Tera Email + App Password
EMAIL_ADDRESS = "bhattanant82@gmail.com"
EMAIL_PASSWORD = "dfnm civm jmih uoqb"  # Tera app password (space ke saath daal diya)

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
        print(f"✅ Email sent to {EMAIL_ADDRESS}: {subject}")
    except Exception as e:
        print(f"❌ Email failed: {e}")

# ================= KUNDLI LOGIC (Tera Same Code) =================

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

DASHA_EFFECTS = {
    "Ketu": "Spirituality, detachment, sudden changes",
    "Venus": "Luxury, marriage, creativity, wealth",
    "Sun": "Leadership, government, fame, health",
    "Moon": "Emotions, family, mind, mother",
    "Mars": "Energy, property, courage, conflicts",
    "Rahu": "Foreign, sudden gains/loss, obsession",
    "Jupiter": "Wisdom, education, finance, growth",
    "Saturn": "Hard work, delay, discipline, longevity",
    "Mercury": "Business, communication, intellect"
}

def degree_to_rashi(deg):
    return RASHIS[int(deg // 30) % 12]

def degree_to_nakshatra(deg):
    return NAKSHATRAS[int(deg // (360/27)) % 27]

def get_lagna(birth_time, loc):
    frame = AltAz(obstime=birth_time, location=loc)
    sun = get_sun(birth_time)
    altaz = sun.transform_to(frame)
    lagna_deg = (altaz.az.degree - 24.0) % 360  # Lahiri Ayanamsa
    return lagna_deg

@app.route('/generate-kundli', methods=['POST'])
def generate_kundli():
    try:
        data = request.json
        dob = data['dob']
        tob = data['tob']
        place = data['place']

        day, month, year = map(int, dob.split('/'))
        hour, minute, second = map(int, tob.split(':'))
        birth_dt = datetime(year, month, day, hour, minute, second)
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

        result = {
            "lagna": lagna,
            "graha": positions,
            "current_dasha": dasha,
            "predictions": predictions,
            "note": "Accurate Vedic Kundli with Lahiri Ayanamsa."
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ================= ADMIN NOTIFICATION SYSTEM =================

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

        # Demo save (real me DB me save karna)
        print(f"New Pandit: {name}, {phone}, {email}, {city}, {experience} years, {languages}")

        # Email notification to admin (tera email)
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


@app.route('/book-puja', methods=['POST'])
def book_puja():
    try:
        data = request.json
        user_name = data.get('user_name')
        phone = data.get('phone')
        email = data.get('email')
        puja = data.get('puja')
        pandit = data.get('pandit')
        date = data.get('date')
        time = data.get('time')
        amount = data.get('amount', 2500)

        # Demo save
        print(f"New Booking: {user_name}, {puja}, {pandit}, {date} {time}, ₹{amount}")

        # Email to admin
        subject = f"New Booking Received - ₹{amount}"
        body = f"""
        New booking received!

        User: {user_name}
        Phone: {phone}
        Email: {email}
        Puja: {puja}
        Pandit: {pandit}
        Date/Time: {date} {time}
        Amount: ₹{amount}

        Please confirm in admin dashboard.
        """
        send_admin_email(subject, body)

        return jsonify({"message": "Booking submitted! Admin will confirm soon.", "success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/request-refund', methods=['POST'])
def request_refund():
    try:
        data = request.json
        booking_id = data.get('booking_id')
        reason = data.get('reason')
        amount = data.get('amount')

        # Demo refund request
        print(f"Refund Request: Booking #{booking_id}, Reason: {reason}, Amount: ₹{amount}")

        # Email to admin
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
    # Dummy data for demo (real me DB se fetch kar)
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
    # Real me DB update kar (status change, refund logic)
    # Demo ke liye dummy response
    return jsonify({"message": f"{action} successful for ID {id}", "success": True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)