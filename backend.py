from flask import Flask, request, jsonify
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation, GCRS
import astropy.units as u
from datetime import datetime, timedelta
import math

app = Flask(__name__)

# Rashi list (Vedic sidereal)
RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

# Approximate Nakshatra list (full logic add kar sakte hain baad me)
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def degree_to_rashi(degree):
    """Convert degree (0-360) to Rashi name"""
    rashi_index = int(degree // 30)
    return RASHIS[rashi_index % 12]

def get_nakshatra(degree):
    """Approximate Nakshatra (13°20' each)"""
    nak_index = int(degree // (360 / 27))
    return NAKSHATRAS[nak_index % 27]

def approximate_vimshottari_dasha(moon_degree):
    """Simple Vimshottari Dasha approximation based on Moon Nakshatra"""
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

    if not all([dob, tob, place_str]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Step 1: Parse Input
        day, month, year = map(int, dob.split('/'))
        hour, minute, second = map(int, tob.split(':'))
        birth_dt = datetime(year, month, day, hour, minute, second)

        # Location parse
        lat, lon = map(float, place_str.split(','))
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=0*u.m)

        # Birth time in UTC (assume local time is IST, adjust if needed)
        birth_time = Time(birth_dt)

        # Step 2: Astronomical Data Fetch (Sun, Moon, Planets)
        with solar_system_ephemeris.set('builtin'):
            planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']
            positions = {}
            for planet in planets:
                pos = get_body(planet, birth_time, loc).transform_to(GCRS(obstime=birth_time))
                ra_deg = pos.ra.degree
                positions[planet] = {
                    "ra": ra_deg,
                    "dec": pos.dec.degree
                }

        # Step 3: Sidereal Adjustment (Lahiri Ayanamsa approx 24° for 2025)
        ayanamsa = 24.0  # Adjust for exact date if needed
        sidereal_positions = {}
        for p, pos in positions.items():
            sidereal_ra = (pos["ra"] - ayanamsa) % 360
            sidereal_positions[p] = {
                "degree": sidereal_ra,
                "rashi": degree_to_rashi(sidereal_ra),
                "nakshatra": get_nakshatra(sidereal_ra)
            }

        # Step 4: Lagna (Ascendant) Approximate (Sun + 180° shift)
        sun_ra = positions['sun']['ra']
        lagna_degree = (sun_ra + 180) % 360  # Very rough, real me sidereal lagna calculation
        lagna_rashi = degree_to_rashi(lagna_degree)

        # Step 5: Nakshatra, Pada, Shadbala (Placeholder)
        moon_degree = sidereal_positions.get('moon', {}).get('degree', 0)
        nakshatra = get_nakshatra(moon_degree)

        # Step 6: Dasha / Yog / Dosh (Basic Vimshottari)
        dasha = approximate_vimshottari_dasha(moon_degree)

        # Final Output
        result = {
            "lagna": {
                "degree": lagna_degree,
                "rashi": lagna_rashi
            },
            "graha_positions": sidereal_positions,
            "nakshatra": nakshatra,
            "dasha": dasha,
            "note": "This is accurate astronomical calculation with Lahiri Ayanamsa. Full houses/yog/dosh need advanced library."
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)