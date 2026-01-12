<?php
session_start();

$email = $_POST['email'] ?? '';
$password = $_POST['password'] ?? '';

// basic validation
if ($email == '' || $password == '') {
    die("Email aur Password dono bharna zaroori hai");
}

// ADMIN LOGIN
if (str_starts_with($email, "admin")) {
    $_SESSION['role'] = 'admin';
    $_SESSION['email'] = $email;
    header("Location: admin/dashboard.php");
    exit;
}

// CUSTOMER LOGIN
else {
    $_SESSION['role'] = 'customer';
    $_SESSION['email'] = $email;
    header("Location: customer/dashboard.php");
    exit;
}
?>