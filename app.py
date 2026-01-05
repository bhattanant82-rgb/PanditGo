from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="panditgo"
)
cursor = db.cursor(dictionary=True)

# 🔔 New Pandit Apply
@app.route('/pandit/apply', methods=['POST'])
def apply_pandit():
    data = request.json
    cursor.execute(
        "INSERT INTO users (name,email,phone,role) VALUES (%s,%s,%s,'pandit')",
        (data['name'], data['email'], data['phone'])
    )
    user_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO pandits (user_id,city,experience,specialization) VALUES (%s,%s,%s,%s)",
        (user_id, data['city'], data['experience'], data['specialization'])
    )
    db.commit()
    return jsonify({"message": "Pandit request submitted"})


# 🟢 Admin – Get Pending Pandits
@app.route('/admin/pandits')
def get_pending_pandits():
    cursor.execute("""
        SELECT pandits.id, users.name, users.phone, pandits.city
        FROM pandits
        JOIN users ON pandits.user_id = users.id
        WHERE pandits.status='pending'
    """)
    return jsonify(cursor.fetchall())


# ✅ Approve Pandit
@app.route('/admin/approve-pandit/<int:id>', methods=['POST'])
def approve_pandit(id):
    cursor.execute("UPDATE pandits SET status='approved' WHERE id=%s", (id,))
    db.commit()
    return jsonify({"success": True})


# 💰 New Booking
@app.route('/booking', methods=['POST'])
def new_booking():
    data = request.json
    cursor.execute("""
        INSERT INTO bookings (user_id,pandit_id,puja_type,amount)
        VALUES (%s,%s,%s,%s)
    """, (data['user_id'], data['pandit_id'], data['puja'], data['amount']))
    db.commit()
    return jsonify({"message": "Booking saved"})


# 🔁 Refund Request
@app.route('/refund', methods=['POST'])
def refund_request():
    data = request.json
    cursor.execute(
        "INSERT INTO refunds (booking_id,reason) VALUES (%s,%s)",
        (data['booking_id'], data['reason'])
    )
    db.commit()
    return jsonify({"message": "Refund requested"})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
