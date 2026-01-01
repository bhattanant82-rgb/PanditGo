from flask import Flask, request, jsonify
from flask_cors import CORS
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body
import astropy.units as u
from datetime import datetime, timedelta
import math

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

@app.route('/generate-kundli', methods=['POST'])
def generate_kundli():
    data = request.json
    dob = data['dob']  # DD/MM/YYYY
    tob = data['tob']  # HH:MM:SS
    place = data['place'].split(',')  # lat, long

    # Step 1: Input Parse
    birth_dt = f"{dob.split('/')[2]}-{dob.split('/')[1]}-{dob.split('/')[0]} {tob}"
    birth_time = Time(birth_dt)

    loc = EarthLocation(lat=float(place[0])*u.deg, lon=float(place[1])*u.deg, height=0*u.m)

    # Step 2: Astronomical Data Fetch
    with solar_system_ephemeris.set('builtin'):
        planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']
        positions = {}
        for planet in planets:
            pos = get_body(planet, birth_time, loc).transform_to(GCRS(obstime=birth_time))
            positions[planet] = pos.ra.degree, pos.dec.degree

    # Step 3: Sidereal Adjustment (Lahiri Ayanamsa approx)
    ayanamsa = 24.0  # For 2025, adjust if needed
    sidereal = {p: ((ra - ayanamsa) % 360, dec) for p, (ra, dec) in positions.items()}

    # Step 4: Lagna / Houses Calculate (Placeholder, full logic for houses)
    sun_pos = get_body('sun', birth_time, loc)
    lagna = (sun_pos.ra.degree + 180) % 360  # Approximate Lagna

    # Step 5: Nakshatra, Pada, Shadbala (Placeholder logic)
    nakshatra = "Calculated Nakshatra"  # Add full logic

    # Step 6: Dasha / Yog / Dosh (Vimshottari placeholder)
    dasha = "Venus Dasha (2025-2045)"  # Add Vimshottari calculation

    # Return JSON
    return jsonify({
        'positions': sidereal,
        'lagna': lagna,
        'nakshatra': nakshatra,
        'dasha': dasha
    })

if __name__ == '__main__':
    app.run(debug=True)