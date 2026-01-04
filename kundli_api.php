<?php
header("Content-Type: application/json");

// 🔐 Prokerala Credentials
$client_id = "8ff2fde0-e9f6-41e5-ba80-adf7032f7a45";
$client_secret = "ZrOfGGigsni5RpDsq3n1S3eH0LMIog29nAjRzAQI";

// STEP 1: Get Access Token
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
  echo json_encode(["error" => "Token error"]);
  exit;
}
$token = $token_data["access_token"];

// STEP 2: Get user input
$dob = $_GET["dob"];
$tob = $_GET["tob"];
$place = urlencode($_GET["place"]);

// STEP 3: Call REAL Kundli API
$url = "https://api.prokerala.com/v2/astrology/kundli?dob=$dob&tob=$tob&place=$place";

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
  "Authorization: Bearer $token"
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$result = curl_exec($ch);
curl_close($ch);

// STEP 4: Send result to frontend
echo $result;
