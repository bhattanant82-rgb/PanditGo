from flask import Flask, request, jsonify, session, render_template, redirect, url_for
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
import jwt
from functools import wraps

app = Flask(__name__, template_folder='templates')  # templates folder bana lena
CORS(app, supports_credentials=True)
app.secret_key = "super_secret_key_2026"
JWT_SECRET = "jwt_secret_2026"

# Gmail SMTP
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

# Database connection
def get_db():
    conn = sqlite3.connect('bookmypandit.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB with full schema
def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('user', 'pandit', 'admin')) DEFAULT 'user',
        status TEXT CHECK(status IN ('active', 'blocked')) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Pandit profiles
    c.execute('''CREATE TABLE IF NOT EXISTS pandit_profiles (
        pandit_id INTEGER PRIMARY KEY,
        city TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        languages TEXT,
        specialization TEXT,
        id_proof_path TEXT,
        bank_upi TEXT,
        rating REAL DEFAULT 0.0,
        total_bookings INTEGER DEFAULT 0,
        total_earnings REAL DEFAULT 0.0,
        pending_payout REAL DEFAULT 0.0,
        status TEXT CHECK(status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
        admin_notes TEXT,
        approved_at TIMESTAMP,
        FOREIGN KEY (pandit_id) REFERENCES users(id) ON DELETE CASCADE
    )''')
    
    # Puja types
    c.execute('''CREATE TABLE IF NOT EXISTS puja_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        base_price INTEGER NOT NULL,
        duration_minutes INTEGER,
        description TEXT,
        is_active INTEGER DEFAULT 1
    )''')
    
    # Bookings
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        pandit_id INTEGER NOT NULL,
        puja_type_id INTEGER NOT NULL,
        booking_date TEXT NOT NULL,
        booking_time TEXT NOT NULL,
        address TEXT NOT NULL,
        total_amount INTEGER NOT NULL,
        advance_paid INTEGER NOT NULL,
        payment_id TEXT,
        status TEXT CHECK(status IN ('pending', 'confirmed', 'completed', 'cancelled')) DEFAULT 'pending',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (pandit_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (puja_type_id) REFERENCES puja_types(id)
    )''')
    
    # Refunds
    c.execute('''CREATE TABLE IF NOT EXISTS refunds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        reason TEXT NOT NULL,
        status TEXT CHECK(status IN ('requested', 'approved', 'rejected')) DEFAULT 'requested',
        razorpay_refund_id TEXT,
        approved_by INTEGER,
        approved_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
        FOREIGN KEY (approved_by) REFERENCES users(id)
    )''')
    
    # Pandit earnings
    c.execute('''CREATE TABLE IF NOT EXISTS pandit_earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pandit_id INTEGER NOT NULL,
        booking_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        commission REAL NOT NULL,
        payout_status TEXT CHECK(payout_status IN ('pending', 'paid')) DEFAULT 'pending',
        paid_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pandit_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
    )''')
    
    # Admin notifications
    c.execute('''CREATE TABLE IF NOT EXISTS admin_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT CHECK(type IN ('new_pandit', 'new_booking', 'refund_request', 'payout_request')) NOT NULL,
        reference_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insert default data
    hashed_admin = sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (name, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)", 
              ("Admin User", "admin@bookmypandit.com", "9999999999", hashed_admin, "admin"))
    
    c.execute("INSERT OR IGNORE INTO puja_types (name, base_price, duration_minutes, description) VALUES (?, ?, ?, ?)", 
              ("Griha Pravesh", 5100, 180, "House warming ceremony"))
    c.execute("INSERT OR IGNORE INTO puja_types (name, base_price, duration_minutes, description) VALUES (?, ?, ?, ?)", 
              ("Satyanarayan Puja", 2500, 120, "Monthly prosperity puja"))
    
    conn.commit()
    conn.close()
    print("Database initialized!")

init_db()

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# User Signup
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = sha256(data.get('password').encode()).hexdigest()
    role = data.get('role', 'user')
    
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)", 
                  (name, email, phone, password, role))
        user_id = c.lastrowid
        if role == 'pandit':
            # Insert pandit profile
            c.execute("INSERT INTO pandit_profiles (pandit_id, city, experience_years, languages, specialization) VALUES (?, ?, ?, ?, ?)", 
                      (user_id, data.get('city'), data.get('experience'), data.get('languages'), data.get('specialization')))
            # Notify admin
            c.execute("INSERT INTO admin_notifications (type, reference_id, message) VALUES (?, ?, ?)", 
                      ('new_pandit', user_id, f'New pandit {name} registered'))
        conn.commit()
        token = jwt.encode({'user_id': user_id, 'role': role}, JWT_SECRET, algorithm="HS256")
        return jsonify({'success': True, 'token': token})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Email or phone already exists'}), 400
    finally:
        conn.close()

# Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier')  # email or phone
    password = sha256(data.get('password').encode()).hexdigest()
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, role FROM users WHERE (email=? OR phone=?) AND password_hash=? AND status='active'", 
              (identifier, identifier, password))
    user = c.fetchone()
    conn.close()
    if user:
        token = jwt.encode({'user_id': user['id'], 'role': user['role']}, JWT_SECRET, algorithm="HS256")
        return jsonify({'success': True, 'token': token, 'role': user['role']})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

# Check Auth
@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'authenticated': False}), 401
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return jsonify({'authenticated': True, 'role': data['role'], 'user_id': data['user_id']})
    except:
        return jsonify({'authenticated': False}), 401

# Get Pujas
@app.route('/api/pujas', methods=['GET'])
def get_pujas():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM puja_types WHERE is_active=1")
    pujas = c.fetchall()
    conn.close()
    return jsonify([dict(puja) for puja in pujas])

# Create Booking
@app.route('/api/bookings', methods=['POST'])
@token_required
def create_booking(current_user):
    data = request.json
    # Assume data has puja_id, date, time, address, etc.
    # For simplicity, insert booking
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO bookings (user_id, pandit_id, puja_type_id, booking_date, booking_time, address, total_amount, advance_paid) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
              (current_user, data['pandit_id'], data['puja_id'], data['date'], data['time'], data['address'], data['amount'], data['advance']))
    booking_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'booking_id': booking_id})

# Get User Bookings
@app.route('/api/bookings', methods=['GET'])
@token_required
def get_bookings(current_user):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE user_id=?", (current_user,))
    bookings = c.fetchall()
    conn.close()
    return jsonify([dict(b) for b in bookings])

# Admin Dashboard Data
@app.route('/api/admin/dashboard', methods=['GET'])
@token_required
def admin_dashboard_data(current_user):
    # Check if admin
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (current_user,))
    user = c.fetchone()
    if user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get stats
    c.execute("SELECT COUNT(*) as total_users FROM users WHERE role='user'")
    total_users = c.fetchone()['total_users']
    c.execute("SELECT COUNT(*) as total_pandits FROM users WHERE role='pandit'")
    total_pandits = c.fetchone()['total_pandits']
    c.execute("SELECT COUNT(*) as total_bookings FROM bookings")
    total_bookings = c.fetchone()['total_bookings']
    c.execute("SELECT SUM(total_amount) as total_revenue FROM bookings WHERE status='completed'")
    total_revenue = c.fetchone()['total_revenue'] or 0
    
    # Recent bookings
    c.execute("SELECT b.*, u.name as user_name, p.name as pandit_name FROM bookings b JOIN users u ON b.user_id=u.id JOIN users p ON b.pandit_id=p.id ORDER BY b.created_at DESC LIMIT 10")
    recent_bookings = c.fetchall()
    
    # Pending pandits
    c.execute("SELECT u.name, pp.* FROM users u JOIN pandit_profiles pp ON u.id=pp.pandit_id WHERE pp.status='pending'")
    pending_pandits = c.fetchall()
    
    conn.close()
    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_pandits': total_pandits,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue
        },
        'recent_bookings': [dict(b) for b in recent_bookings],
        'pending_pandits': [dict(p) for p in pending_pandits]
    })

# Approve Pandit
@app.route('/api/admin/approve-pandit/<int:pandit_id>', methods=['POST'])
@token_required
def approve_pandit(current_user, pandit_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE id=?", (current_user,))
    if c.fetchone()['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    c.execute("UPDATE pandit_profiles SET status='approved', approved_at=CURRENT_TIMESTAMP WHERE pandit_id=?", (pandit_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Refund Route
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

# Kundli Generator
RASHIS = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

def degree_to_rashi(deg):
    return RASHIS[int(deg // 30) % 12]

def degree_to_nakshatra(deg):
    return NAKSHATRAS[int(deg // (360/27)) % 27]

DASHA_EFFECTS = {
    0: "Strong spiritual growth",
    1: "Career advancement",
    2: "Family harmony",
    3: "Financial stability",
    4: "Health improvements",
    5: "Relationship success",
    6: "Learning and wisdom",
    7: "Leadership qualities",
    8: "Completion and new beginnings"
}

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

# Admin Login (now with JWT)
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    email = data.get("email")
    password = sha256(data.get("password").encode()).hexdigest()
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT id FROM users WHERE email=? AND password_hash=? AND role='admin'",
        (email, password)
    )
    admin = c.fetchone()
    conn.close()
    if admin:
        token = jwt.encode({'user_id': admin['id'], 'role': 'admin'}, JWT_SECRET, algorithm="HS256")
        return jsonify({"success": True, "token": token})
    return jsonify({"success": False}), 401

# Admin Dashboard Page (serve static HTML, auth checked in JS)
@app.route("/admin-dashboard")
def admin_dashboard():
    return send_from_directory('.', 'admin dashboard/admin.html')

# Logout (for session if used)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Run
if __name__ == "__main__":
    app.run(debug=True, port=5000)