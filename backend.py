from flask import Flask, request, jsonify
from flask_cors import CORS
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body
import astropy.units as u
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ================= DATA =================

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
    "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

DASHA_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

# ================= HELPERS =================

def degree_to_rashi(deg):
    return RASHIS[int(deg // 30) % 12]

def get_nakshatra(deg):
    return NAKSHATRAS[int(deg // (360/27)) % 27]

def vimshottari_dasha(moon_deg):
    index = int(moon_deg // (360/27)) % 9
    lord = DASHA_LORDS[index]

    dasha_map = {
        "Venus": "Good for career growth, marriage & luxury",
        "Sun": "Authority, government, leadership focus",
        "Moon": "Emotions, mind, family matters",
        "Mars": "Energy, property, conflicts possible",
        "Rahu": "Sudden changes, foreign links",
        "Jupiter": "Education, wisdom, finance",
        "Saturn": "Hard work, delay, stability",
        "Mercury": "Business, communication",
        "Ketu": "Spirituality, detachment"
    }

    return {
        "mahadasha": lord,
        "meaning": dasha_map.get(lord)
    }

def future_predictions(lagna_rashi):
    predictions = {
        "career": f"As {lagna_rashi.split()[0]} Lagna, leadership, management, IT, business or government roles are favourable.",
        "money": "Steady income indicated. Best period for savings and long-term investments. Avoid speculation.",
        "marriage": "Marriage prospects improve after mid-dasha change. Partner will be supportive but emotional.",
        "health": "Generally good health. Watch stress, digestion and head-related issues."
    }
    return predictions

# ================= API =================

@app.route("/generate-kundli", methods=["POST"])
def generate_kundli():
    try:
        data = request.json

        # Parse input
        day, month, year = map(int, data["dob"].split("/"))
        hour, minute, second = map(int, data["tob"].split(":"))
        lat, lon = map(float, data["place"].split(","))

        birth_dt = datetime(year, month, day, hour, minute, second)
        t = Time(birth_dt)

        ayanamsa = 24.0  # Lahiri approx

        planets = ["sun","moon","mars","mercury","venus","jupiter","saturn"]
        positions = {}

        with solar_system_ephemeris.set("builtin"):
            for p in planets:
                body = get_body(p, t)
                deg = (body.ra.degree - ayanamsa) % 360
                positions[p] = {
                    "degree": round(deg,2),
                    "rashi": degree_to_rashi(deg),
                    "nakshatra": get_nakshatra(deg)
                }

        # Lagna (simplified but stable)
        lagna_deg = (t.sidereal_time("mean", lon*u.deg).degree) % 360
        lagna_rashi = degree_to_rashi(lagna_deg)

        dasha = vimshottari_dasha(positions["moon"]["degree"])
        predictions = future_predictions(lagna_rashi)

        return jsonify({
            "lagna": {
                "degree": round(lagna_deg,2),
                "rashi": lagna_rashi
            },
            "planets": positions,
            "dasha": dasha,
            "predictions": predictions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
