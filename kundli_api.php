<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header("Content-Type: application/json");

// 🔐 Prokerala Credentials (TERE HI)
$client_id = "8ff2fde0-e9f6-41e5-ba80-adf7032f7a45";
$client_secret = "ZrOfGGigsni5RpDsq3n1S3eH0LMIog29nAjRzAQI";

// ===============================
// STEP 1: GET ACCESS TOKEN
// ===============================
$token_url = "https://api.prokerala.com/token";

$ch = curl_init($token_url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([
  "grant_type" => "client_credentials",
  "client_id" => $client_id,
  "client_secret" => $client_secret
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

$token_data = json_decode($response, true);
if (!isset($token_data["access_token"])) {
  echo json_encode([
    "error" => "Token error",
    "raw" => $token_data
  ]);
  exit;
}
$token = $token_data["access_token"];

// ===============================
// STEP 2: USER INPUT
// ===============================
$dob = $_GET["dob"];   // YYYY-MM-DD
$tob = $_GET["tob"];   // HH:MM
$place = $_GET["place"]; // currently unused (next upgrade)

// ===============================
// STEP 3: REQUIRED PARAMETERS
// ===============================

// 🔴 TEMP FIX: STATIC COORDINATES (Ahmedabad)
// Later we will auto-detect from city
$coordinates = "23.0225,72.5714";

// ✅ Correct datetime format (ISO 8601)
$datetime = $dob . "T" . $tob . ":00+05:30";

// ✅ Lahiri Ayanamsa (STANDARD VEDIC)
$ayanamsa = 1;

// ===============================
// STEP 4: CALL REAL KUNDLI API
// ===============================
$url = "https://api.prokerala.com/v2/astrology/kundli"
     . "?datetime=" . urlencode($datetime)
     . "&coordinates=" . urlencode($coordinates)
     . "&ayanamsa=" . $ayanamsa;

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
  "Authorization: Bearer $token"
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$result = curl_exec($ch);
curl_close($ch);

// ===============================
// STEP 5: SEND TO FRONTEND
// ===============================
echo $result;
