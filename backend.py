from flask import Flask, request, jsonify, session
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
import sqlite3
from hashlib import sha256

app = Flask(__name__)
CORS(app)
app.secret_key = "super_secret_key_2026"  # Production me change kar dena

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
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Email failed: {e}")

# Database connection
def get_db():
    conn = sqlite3.connect('bookmypandit.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB (ek baar chala dena ya comment out kar dena)
def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS pandits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT,
        experience INTEGER,
        languages TEXT,
        specialization TEXT,
        id_proof TEXT,
        bank_details TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Sample admin (password: admin123)
    hashed = sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO admins (email, password_hash) VALUES (?, ?)", 
              ("admin@bookmypandit.com", hashed))
    conn.commit()
    conn.close()
    print("Database initialized!")

# Razorpay Refund
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

# Kundli Generator (simplified - astropy without get_moon error)
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

        # Simplified lagna
        sun_ra = get_body('sun', birth_time, loc).ra.degree
        lagna_deg = (sun_ra - 24.0) % 360
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

# Admin Login (hashed password)
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    hashed = sha256(password.encode()).hexdigest()

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM admins WHERE email = ? AND password_hash = ?", (email, hashed))
    admin = c.fetchone()
    conn.close()

    if admin:
        session['admin_id'] = admin['id']
        return jsonify({"success": True, "message": "Admin login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

# Pandit Join (save with pending status)
@app.route('/become-pandit', methods=['POST'])
def become_pandit():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    city = data.get('city')
    experience = data.get('experience')
    languages = data.get('languages')
    specialization = data.get('specialization')

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO pandits (name, phone, email, city, experience, languages, specialization, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (name, phone, email, city, experience, languages, specialization))
        conn.commit()
        return jsonify({"success": True, "message": "Application submitted! Admin will review."})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Phone or email already registered"}), 400
    finally:
        conn.close()

# Admin approve pandit
@app.route('/admin/approve-pandit', methods=['POST'])
def approve_pandit():
    if 'admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    pandit_id = data.get('pandit_id')

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE pandits SET status = 'approved' WHERE id = ?", (pandit_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Pandit approved! Dashboard unlocked."})

# Get pending pandits (admin only)
@app.route('/admin/pending-pandits', methods=['GET'])
def get_pending_pandits():
    if 'admin_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM pandits WHERE status = 'pending'")
    pandits = [dict(row) for row in c.fetchall()]
    conn.close()

    return jsonify(pandits)

# Pandit status check
@app.route('/pandit/check-status', methods=['POST'])
def pandit_check_status():
    data = request.json
    phone = data.get('phone')

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT status FROM pandits WHERE phone = ?", (phone,))
    result = c.fetchone()
    conn.close()

    if result:
        return jsonify({"status": result['status']})
    return jsonify({"status": "not_found"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)