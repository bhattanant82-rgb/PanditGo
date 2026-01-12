<?php
session_start();

// Simple validation - in real app, check against database
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $identifier = trim($_POST['identifier'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if (empty($identifier) || empty($password)) {
        echo json_encode(['success' => false, 'error' => 'All fields are required']);
        exit;
    }

    // For demo: accept any non-empty credentials
    if (!empty($identifier) && !empty($password)) {
        $_SESSION['email'] = $identifier;
        $_SESSION['role'] = 'pandit';
        echo json_encode(['success' => true, 'redirect' => 'pandit-dashboard.php']);
    } else {
        echo json_encode(['success' => false, 'error' => 'Invalid credentials']);
    }
} else {
    echo json_encode(['success' => false, 'error' => 'Invalid request method']);
}
?>