<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");

$client_id = "bff2fdee-e9f6-41e5-ba80-adf7032f7a45";  // New from screenshot
$client_secret = "ZrOfGGigsni5RpDsq3n1S3eH0LMIog29nAjRzAQI";  // New from screenshot

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
    echo json_encode(["error" => "Token generation failed", "details" => $token_data]);
    exit;
}
$token = $token_data["access_token"];

$dob = $_GET["dob"] ?? "";
$tob = $_GET["tob"] ?? "";
$place = $_GET["place"] ?? "23.0225,72.5714";

if (empty($dob) || empty($tob)) {
    echo json_encode(["error" => "DOB or TOB missing"]);
    exit;
}

# DOB DD/MM/YYYY to YYYY-MM-DD
$dob_parts = explode('/', $dob);
$dob_iso = $dob_parts[2] . '-' . $dob_parts[1] . '-' . $dob_parts[0];

$datetime = $dob_iso . "T" . $tob . ":00+05:30";

$url = "https://api.prokerala.com/v2/astrology/kundli?datetime=" . urlencode($datetime) . "&coordinates=" . urlencode($place) . "&ayanamsa=1";

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Authorization: Bearer $token"]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$result = curl_exec($ch);
curl_close($ch);

echo $result;