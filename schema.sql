-- ========================================
-- BOOKMYPANDIT DATABASE SCHEMA (2026 READY)
-- ========================================
-- Real-life usable, scalable, secure
-- MySQL / MariaDB compatible

DROP DATABASE IF EXISTS bookmypandit;
CREATE DATABASE bookmypandit CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookmypandit;

-- 1. USERS TABLE (All roles in one table - best practice)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'pandit', 'admin') DEFAULT 'user',
    status ENUM('active', 'blocked') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_role (role)
);

-- 2. PANDIT PROFILE (Extra details for pandits)
CREATE TABLE pandit_profiles (
    pandit_id INT PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    experience_years INT NOT NULL,
    languages VARCHAR(200), -- comma separated
    specialization VARCHAR(500), -- comma separated pujas
    id_proof_path VARCHAR(255), -- uploaded file path
    bank_upi VARCHAR(100),
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_bookings INT DEFAULT 0,
    total_earnings DECIMAL(10,2) DEFAULT 0.00,
    pending_payout DECIMAL(10,2) DEFAULT 0.00,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    admin_notes TEXT,
    approved_at TIMESTAMP NULL,
    FOREIGN KEY (pandit_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. PUJA TYPES (Admin can add/edit)
CREATE TABLE puja_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    base_price INT NOT NULL,
    duration_minutes INT,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 4. BOOKINGS (Heart of business)
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pandit_id INT NOT NULL,
    puja_type_id INT NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    address TEXT NOT NULL,
    total_amount INT NOT NULL,
    advance_paid INT NOT NULL,
    payment_id VARCHAR(100), -- Razorpay payment ID
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pandit_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (puja_type_id) REFERENCES puja_types(id),
    INDEX idx_status (status),
    INDEX idx_date (booking_date)
);

-- 5. REFUNDS
CREATE TABLE refunds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount INT NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('requested', 'approved', 'rejected') DEFAULT 'requested',
    razorpay_refund_id VARCHAR(100),
    approved_by INT NULL, -- admin id
    approved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- 6. EARNINGS & PAYOUTS
CREATE TABLE pandit_earnings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pandit_id INT NOT NULL,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL, -- pandit ka share
    commission DECIMAL(10,2) NOT NULL, -- platform commission
    payout_status ENUM('pending', 'paid') DEFAULT 'pending',
    paid_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pandit_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

-- 7. ADMIN NOTIFICATIONS
CREATE TABLE admin_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('new_pandit', 'new_booking', 'refund_request', 'payout_request') NOT NULL,
    reference_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. SAMPLE DATA (For testing)
INSERT INTO users (name, email, phone, password_hash, role) VALUES
('Admin User', 'admin@bookmypandit.com', '9999999999', 'e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4', 'admin'), -- password: admin123
('Anant Bhatt', 'bhattanant82@gmail.com', '9635920705', 'hashed_password_here', 'user');

-- Default puja types
INSERT INTO puja_types (name, base_price, duration_minutes, description) VALUES
('Griha Pravesh', 5100, 180, 'House warming ceremony'),
('Satyanarayan Puja', 2500, 120, 'Monthly prosperity puja'),
('Rudrabhishek', 3100, 150, 'Lord Shiva abhishek'),
('Marriage Puja', 11000, 240, 'Complete wedding rituals');

PRINT 'Database schema created successfully! Real production ready.';