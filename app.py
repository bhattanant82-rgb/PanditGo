from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import jwt  # pip install pyjwt

app = Flask(__name__)
CORS(app)

# Change these as per your setup
DB_CONFIG = {
    "host": "localhost",
    "database": "panditgo_db",
    "user": "postgres",          # YOUR username
    "password": "your_password"  # YOUR password
}

SECRET_KEY = "panditgo_secret_key_2026"  # Change in production

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# ------------------ ROLE-BASED LOGIN ------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')
    password = data.get('password')  # In real project use hashed comparison

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Check in all 3 tables (customer, pandit, admin)
    cur.execute("""
        SELECT id, name, 'customer' as role 
        FROM users 
        WHERE (email = %s OR phone = %s) AND password_hash = %s
        
        UNION
        
        SELECT id, name, 'pandit' as role 
        FROM pandits 
        WHERE (email = %s OR phone = %s) AND password_hash = %s
        
        UNION
        
        SELECT id, name, 'admin' as role 
        FROM admins 
        WHERE email = %s AND password_hash = %s
    """, (identifier, identifier, password, identifier, identifier, password, identifier, password))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        token = jwt.encode({
            'user_id': user['id'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            'success': True,
            'token': token,
            'role': user['role'],
            'name': user['name']
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# ------------------ LIVE STATS (FOR REAL-TIME DASHBOARD) ------------------
@app.route('/api/live-stats', methods=['GET'])
def get_live_stats():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Total users
    cur.execute("SELECT COUNT(*) as count FROM users")
    total_users = cur.fetchone()['count']

    # Active users (booked or logged in last 24h - assuming last_active column)
    cur.execute("""
        SELECT COUNT(DISTINCT user_id) as count 
        FROM bookings 
        WHERE booking_date >= %s
    """, (datetime.now() - timedelta(days=1),))
    active_users = cur.fetchone()['count']

    # Pending pandits
    cur.execute("SELECT COUNT(*) as count FROM pandits WHERE status = 'pending'")
    pending_pandits = cur.fetchone()['count']

    # Total revenue
    cur.execute("SELECT COALESCE(SUM(amount), 0) as total FROM bookings WHERE status = 'completed'")
    total_revenue = cur.fetchone()['total']

    # Recent new pandits (last 5 pending)
    cur.execute("""
        SELECT id, name, email, phone, experience_years, specialization, status, submitted_at 
        FROM pandits 
        WHERE status = 'pending' 
        ORDER BY submitted_at DESC LIMIT 5
    """)
    new_pandits = cur.fetchall()

    # Recent new bookings (last 5)
    cur.execute("""
        SELECT id, user_name, pandit_name, service, booking_date, status, amount 
        FROM bookings 
        ORDER BY booking_date DESC LIMIT 5
    """)
    new_bookings = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "total_users": total_users,
        "active_users": active_users,
        "pending_pandits": pending_pandits,
        "total_revenue": total_revenue,
        "new_pandits": new_pandits,
        "new_bookings": new_bookings
    })

# ------------------ PANDIT APPROVE / REJECT ------------------
@app.route('/api/pandits/approve/<int:pandit_id>', methods=['POST'])
def approve_pandit(pandit_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE pandits SET status = 'approved' WHERE id = %s", (pandit_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Pandit approved successfully"})

@app.route('/api/pandits/reject/<int:pandit_id>', methods=['POST'])
def reject_pandit(pandit_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE pandits SET status = 'rejected' WHERE id = %s", (pandit_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Pandit rejected"})

# ------------------ OTHER ENDPOINTS (ALREADY WERE THERE) ------------------
@app.route('/api/pandits', methods=['GET'])
def get_pandits():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM pandits ORDER BY submitted_at DESC")
    pandits = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(pandits)

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM bookings ORDER BY booking_date DESC LIMIT 20")
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(bookings)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)