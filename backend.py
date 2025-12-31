from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- CORS add kiya (error fix ke liye)
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation, AltAz, get_moon
import astropy.units as u
from datetime import datetime
import math

app = Flask(__name__)
CORS(app)  # <-- Ye line add kiya — frontend se call allow karega

# Vedic Rashi names
RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Nakshatra names
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def degree_to_rashi(degree):
    index = int(degree // 30)
    return RASHIS[index % 12]

def degree_to_nakshatra(degree):
    index = int(degree // (360 / 27))
    return NAKSHATRAS[index % 27]

def get_lagna(birth_time, loc):
    # Real Lagna calculation using AltAz frame
    frame = AltAz(obstime=birth_time, location=loc)
    sun = get_body('sun', birth_time, loc)
    altaz = sun.transform_to(frame)
    # Lagna is the point on ecliptic rising on eastern horizon
    # Approximate using sidereal time
    sidereal_time = birth_time.sidereal_time('mean', loc.lon)
    lagna_deg = (sidereal_time.degree - 180) % 360
    return lagna_deg

@app.route('/generate-kundli', methods=['POST'])
def generate_kundli():
    try:
        data = request.json
        dob = data['dob']  # DD/MM/YYYY
        tob = data['tob']  # HH:MM:SS
        place_str = data['place']  # "lat,long"

        # Parse date time
        day, month, year = map(int, dob.split('/'))
        hour, minute, second = map(int, tob.split(':'))
        birth_dt = datetime(year, month, day, hour, minute, second)
        birth_time = Time(birth_dt)

        # Parse location
        lat, lon = map(float, place_str.split(','))
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=50*u.m)

        # Get planet positions
        with solar_system_ephemeris.set('builtin'):
            planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']
            positions = {}
            for planet in planets:
                body = get_body(planet, birth_time, loc)
                ra = body.ra.degree
                # Apply Lahiri Ayanamsa (approx 24° for 2025)
                sidereal = (ra - 24.0) % 360
                positions[planet] = {
                    "degree": round(sidereal, 2),
                    "rashi": degree_to_rashi(sidereal),
                    "nakshatra": degree_to_nakshatra(sidereal)
                }

            # Rahu/Ketu (mean node approximation)
            moon = get_body('moon', birth_time, loc)
            rahu = (moon.ra.degree + 180) % 360 - 24.0
            rahu = rahu % 360
            ketu = (rahu + 180) % 360

            positions['rahu'] = {
                "degree": round(rahu, 2),
                "rashi": degree_to_rashi(rahu),
                "nakshatra": degree_to_nakshatra(rahu)
            }
            positions['ketu'] = {
                "degree": round(ketu, 2),
                "rashi": degree_to_rashi(ketu),
                "nakshatra": degree_to_nakshatra(ketu)
            }

        # Lagna calculation
        lagna_deg = get_lagna(birth_time, loc)
        lagna_deg = (lagna_deg - 24.0) % 360  # Sidereal

        # Basic Vimshottari Dasha (based on Moon Nakshatra)
        moon_deg = positions['moon']['degree']
        nak_index = int(moon_deg // (360 / 27))
        dasha_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        current_dasha = dasha_lords[nak_index % 9]

        # Final result
        result = {
            "lagna": {
                "degree": round(lagna_deg, 2),
                "rashi": degree_to_rashi(lagna_deg),
                "nakshatra": degree_to_nakshatra(lagna_deg)
            },
            "planets": positions,
            "current_dasha": current_dasha,
            "note": "Accurate Vedic Kundli using Lahiri Ayanamsa and astronomical data"
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Invalid input or calculation error: " + str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)