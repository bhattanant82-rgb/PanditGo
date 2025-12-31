from flask import Flask, request, jsonify
from flask_cors import CORS  # CORS add kiya — frontend connect issue fix
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation, GCRS
import astropy.units as u
from datetime import datetime, timedelta
import math

app = Flask(__name__)
CORS(app)  # CORS enable — ab frontend se call aayega

# Rashi and Nakshatra lists
RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def degree_to_rashi(degree):
    rashi_index = int(degree // 30)
    return RASHIS[rashi_index % 12]

def get_nakshatra(degree):
    nak_index = int(degree // (360 / 27))
    return NAKSHATRAS[nak_index % 27]

def approximate_vimshottari_dasha(moon_degree):
    nak_index = int(moon_degree // (360 / 27))
    dasha_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_periods = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # years
    lord = dasha_lords[nak_index % 9]
    return f"Current Dasha: {lord} (approx {dasha_periods[nak_index % 9]} years remaining)"

@app.route('/generate-kundli', methods=['POST'])
def generate_kundli():
    data = request.json
    dob = data.get('dob')  # DD/MM/YYYY
    tob = data.get('tob')  # HH:MM:SS
    place_str = data.get('place')  # "lat,long"

    if not dob or not tob or not place_str:
        return jsonify({"error": "All fields are required"}), 400

    try:
        # Step 1: Input Parse
        day, month, year = map(int, dob.split('/'))
        hour, minute, second = map(int, tob.split(':'))
        birth_dt = datetime(year, month, day, hour, minute, second)
        birth_time = Time(birth_dt)

        # Location
        lat, lon = map(float, place_str.split(','))
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=0*u.m)

        # Step 2: Astronomical Data Fetch
        with solar_system_ephemeris.set('builtin'):
            planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']
            positions = {}
            for planet in planets:
                pos = get_body(planet, birth_time, loc).transform_to(GCRS(obstime=birth_time))
                ra_deg = pos.ra.degree
                positions[planet] = ra_deg

        # Step 3: Sidereal Adjustment
        ayanamsa = 24.0
        sidereal_positions = {p: (ra - ayanamsa) % 360 for p, ra in positions.items()}

        # Step 4: Lagna (Ascendant) Calculation
        frame = AltAz(obstime=birth_time, location=loc)
        lagna = get_body('sun', birth_time, loc).transform_to(frame)
        lagna_deg = (lagna.az.degree - ayanamsa) % 360  # Adjusted Lagna

        # Step 5: Nakshatra, Pada (using Moon)
        moon_deg = sidereal_positions['moon']
        nakshatra = get_nakshatra(moon_deg)

        # Step 6: Dasha / Yog / Dosh
        dasha = approximate_vimshottari_dasha(moon_deg)

        # Result
        result = {
            'positions': {p: {"degree": round(deg, 2), "rashi": degree_to_rashi(deg), "nakshatra": get_nakshatra(deg)} for p, deg in sidereal_positions.items()},
            'lagna': {"degree": round(lagna_deg, 2), "rashi": degree_to_rashi(lagna_deg)},
            'nakshatra': nakshatra,
            'dasha': dasha
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)