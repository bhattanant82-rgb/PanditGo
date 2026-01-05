import sqlite3

def init_db():
    conn = sqlite3.connect('bookmypandit.db')
    c = conn.cursor()

    # Pandits table (status: pending / approved / rejected)
    c.execute('''CREATE TABLE IF NOT EXISTS pandits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT,
        experience INTEGER,
        languages TEXT,
        specialization TEXT,
        id_proof TEXT,  -- file path
        bank_details TEXT,
        status TEXT DEFAULT 'pending',  -- pending / approved / rejected
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Admin table (simple, password hashed)
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )''')

    # Sample admin (password: admin123 hashed)
    from hashlib import sha256
    hashed = sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO admins (email, password_hash) VALUES (?, ?)", 
              ("admin@bookmypandit.com", hashed))

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()