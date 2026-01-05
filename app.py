from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import razorpay
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'panditgo_admin_god_mode_2026'  # Change in production
CORS(app)

# Razorpay setup (tera keys daal – test mode me rakh)
razorpay_client = razorpay.Client(auth=("rzp_live_RwBuGYKySb2uQY", "YOUR_RAZORPAY_TEST_KEY_SECRET"))

# DB connection (database.py style)
def get_db():
    conn = sqlite3.connect('panditgo.db')
    conn.row_factory = sqlite3.Row
    return conn

# Admin Login Route
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Real me hashed check kar, abhi mock
    if email == 'admin@panditgo.com' and password == 'admin@123.com':
        session['admin_logged_in'] = True
        return jsonify({'status': 'success', 'message': 'God Mode Activated!'})
    return jsonify({'status': 'error', 'message': 'Invalid Admin Credentials'}), 401

# Admin Logout
@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged_in', None)
    return jsonify({'status': 'success', 'message': 'Logged Out'})

# Check Admin Session (for protection)
def is_admin_logged_in():
    return session.get('admin_logged_in', False)

# Live Stats Route
@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    conn = get_db()
    cursor = conn.cursor()

    # Example stats (real me queries kar)
    total_bookings = cursor.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    revenue = cursor.execute("SELECT SUM(amount) FROM payments WHERE status = 'paid'").fetchone()[0] or 0

    stats = {
        'total_bookings': total_bookings or 1245,
        'today_revenue': 420000,
        'monthly_revenue': 2800000,
        'pending_bookings': 87,
        'active_pandits': 512,
        'new_users': 45
    }
    return jsonify(stats)

# Bookings Management Routes
@app.route('/api/admin/bookings', methods=['GET'])
def view_bookings():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    conn = get_db()
    bookings = conn.execute("SELECT * FROM bookings").fetchall()
    return jsonify([dict(row) for row in bookings])

@app.route('/api/admin/booking/approve', methods=['POST'])
def approve_booking():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    data = request.json
    booking_id = data['booking_id']
    pandit_id = data['pandit_id']

    conn = get_db()
    conn.execute("UPDATE bookings SET status = 'approved', pandit_id = ? WHERE id = ?", (pandit_id, booking_id))
    conn.commit()
    return jsonify({'status': 'success', 'message': 'Booking Approved'})

@app.route('/api/admin/booking/refund', methods=['POST'])
def force_refund():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    data = request.json
    payment_id = data['payment_id']
    amount = data['amount'] * 100  # Paisa me

    try:
        refund = razorpay_client.refund.create({
            "payment_id": payment_id,
            "amount": amount
        })
        return jsonify({'status': 'success', 'refund_id': refund['id']})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Pandit Management
@app.route('/api/admin/pandits/applications', methods=['GET'])
def pandit_applications():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    # Real query
    return jsonify({'applications': [{'id': 1, 'name': 'Sharma Ji', 'status': 'pending'}]})

@app.route('/api/admin/pandit/approve', methods=['POST'])
def approve_pandit():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    data = request.json
    pandit_id = data['pandit_id']
    # Update DB
    return jsonify({'status': 'success', 'message': 'Pandit Approved'})

# User Management
@app.route('/api/admin/users', methods=['GET'])
def view_users():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    # Real query
    return jsonify({'users': [{'id': 1, 'name': 'Ramesh', 'email': 'ramesh@example.com'}]})

@app.route('/api/admin/user/block', methods=['POST'])
def block_user():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    data = request.json
    user_id = data['user_id']
    # Update DB
    return jsonify({'status': 'success', 'message': 'User Blocked'})

# Payment Control
@app.route('/api/admin/payments/reports', methods=['GET'])
def payment_reports():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    # Real Razorpay call if needed
    return jsonify({'reports': [{'date': '2026-01-05', 'amount': 420000}]})

# Puja Control
@app.route('/api/admin/pujas', methods=['GET'])
def get_pujas():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    conn = get_db()
    pujas = conn.execute("SELECT * FROM pujas").fetchall()
    return jsonify([dict(row) for row in pujas])

@app.route('/api/admin/puja/edit', methods=['POST'])
def edit_puja():
    if not is_admin_logged_in():
        return jsonify({'error': 'Access Denied'}), 401

    data = request.json
    puja_id = data['id']
    name = data['name']
    price = data['price']

    conn = get_db()
    conn.execute("UPDATE pujas SET name = ?, price = ? WHERE id = ?", (name, price, puja_id))
    conn.commit()
    return jsonify({'status': 'success', 'message': 'Puja Updated'})

# Puja page ke liye API (pujas.html se call karega)
@app.route('/api/pujas/public', methods=['GET'])
def public_pujas():
    conn = get_db()
    pujas = conn.execute("SELECT * FROM pujas").fetchall()
    return jsonify([dict(row) for row in pujas])

# Initial DB setup (run once)
with get_db() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY, puja TEXT, status TEXT, pandit_id INTEGER, amount REAL)
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pandits (id INTEGER PRIMARY KEY, name TEXT, status TEXT)
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, booking_id INTEGER, status TEXT, amount REAL)
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pujas (id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT)
    ''')
    # Dummy data add
    conn.execute("INSERT OR IGNORE INTO pujas (id, name, price, description) VALUES (1, 'Griha Pravesh', 4999, 'House warming puja')")

if __name__ == '__main__':
    app.run(debug=True, port=5000)