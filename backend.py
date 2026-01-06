from flask import Flask, request, jsonify, session, render_template, redirect
from flask_cors import CORS
import sqlite3
from hashlib import sha256
from datetime import datetime

# =========================
# APP CONFIG
# =========================
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "super_secret_key_2026"

# =========================
# DATABASE
# =========================
def get_db():
    conn = sqlite3.connect("bookmypandit.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Admins
    c.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT
    )
    """)

    # Pandits
    c.execute("""
    CREATE TABLE IF NOT EXISTS pandits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        city TEXT,
        experience INTEGER,
        languages TEXT,
        specialization TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Earnings
    c.execute("""
    CREATE TABLE IF NOT EXISTS earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pandit_id INTEGER,
        booking_id TEXT,
        amount INTEGER,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Default Admin
    admin_pass = sha256("admin123".encode()).hexdigest()
    c.execute(
        "INSERT OR IGNORE INTO admins (email, password_hash) VALUES (?,?)",
        ("admin@panditgo.com", admin_pass)
    )

    conn.commit()
    conn.close()

init_db()

# =========================
# PUBLIC / PAGE ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# -------- ADMIN PAGES --------
@app.route("/admin-login")
def admin_login_page():
    return render_template("admin-login.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect("/admin-login")
    return render_template("admin-dashboard.html")

# -------- PANDIT PAGES --------
@app.route("/pandit-dashboard")
def pandit_dashboard():
    return render_template("pandit-dashboard.html")

@app.route("/earnings")
def earnings_page():
    return render_template("earnings.html")

@app.route("/my-bookings")
def my_bookings_page():
    return render_template("my-bookings.html")

@app.route("/profile")
def profile_page():
    return render_template("profile.html")

# =========================
# ADMIN AUTH APIs
# =========================
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    email = data.get("email")
    password = sha256(data.get("password").encode()).hexdigest()

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM admins WHERE email=? AND password_hash=?",
        (email, password)
    )
    admin = c.fetchone()
    conn.close()

    if admin:
        session["admin_id"] = admin["id"]
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({"success": True})

# =========================
# PANDIT JOIN
# =========================
@app.route("/api/pandit/join", methods=["POST"])
def pandit_join():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO pandits (name, phone, email, city, experience, languages, specialization)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"],
            data["phone"],
            data["email"],
            data["city"],
            data["experience"],
            data["languages"],
            data["specialization"]
        ))
        conn.commit()
        return jsonify({"success": True, "message": "Pandit application submitted"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Phone or Email already exists"}), 400
    finally:
        conn.close()

# =========================
# ADMIN → APPROVE PANDIT
# =========================
@app.route("/api/admin/approve-pandit", methods=["POST"])
def approve_pandit():
    if "admin_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    pandit_id = request.json.get("pandit_id")

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE pandits SET status='approved' WHERE id=?", (pandit_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

# =========================
# PANDIT STATUS CHECK
# =========================
@app.route("/api/pandit/status", methods=["POST"])
def pandit_status():
    phone = request.json.get("phone")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT status FROM pandits WHERE phone=?", (phone,))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({"status": row["status"]})
    return jsonify({"status": "not_found"})

# =========================
# PANDIT EARNINGS API
# =========================
@app.route("/api/pandit/earnings/<int:pandit_id>")
def pandit_earnings(pandit_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM earnings WHERE pandit_id=?", (pandit_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

# =========================
# DEV / TEST
# =========================

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    email = data.get("email")
    password = sha256(data.get("password").encode()).hexdigest()

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM admins WHERE email=? AND password_hash=?",
        (email, password)
    )
    admin = c.fetchone()
    conn.close()

    if admin:
        session["admin_id"] = admin["id"]
        return jsonify({"success": True})

    return jsonify({"success": False}), 401
@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect("/admin-login")
    return render_template("admin-dashboard.html")
@app.route("/api/dev/add-earning")
def add_dummy_earning():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO earnings (pandit_id, booking_id, amount, status)
        VALUES (1, 'BK1001', 5500, 'paid')
    """)
    conn.commit()
    conn.close()
    return "Dummy earning added"

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
