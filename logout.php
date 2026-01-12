<?php
session_start();
$role = $_SESSION['role'] ?? '';
session_destroy();
if ($role === 'pandit') {
    header("Location: pandit-login.html");
} else {
    header("Location: login.php");
}
exit;
?>