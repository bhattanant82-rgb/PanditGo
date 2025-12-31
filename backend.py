from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation
import astropy.units as u
from datetime import datetime
import math

app = Flask(__name__)
CORS(app)

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

def degree_to_rashi(deg):
    return RASHIS[int(deg // 30) % 12]

def get_nakshatra(deg):
    return NAKSHATRAS[int(deg // (360/27)) % 27]

def vimshottari_dasha(moon_deg):
    lords = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
    index = int(moon_deg // (360/27)) % 9
    return f"Current Mahadasha: {lords[index]}"

@app.route('/generate-kundli', methods=['POST'])
def generate_kundli():
    data = request.json

    try:
        day, month, year = map(int, data['dob'].split('/'))
        hour, minute, second = map(int, data['tob'].split(':'))
        lat, lon = map(float, data['place'].split(','))

        birth_dt = datetime(year, month, day, hour, minute, second)
        t = Time(birth_dt)
        location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg)

        positions = {}
        with solar_system_ephemeris.set('builtin'):
            for planet in ['sun','moon','mars','mercury','venus','jupiter','saturn']:
                body = get_body(planet, t)
                lon_deg = body.ra.degree
                sidereal = (lon_deg - 24) % 360
                positions[planet] = {
                    "degree": round(sidereal,2),
                    "rashi": degree_to_rashi(sidereal),
                    "nakshatra": get_nakshatra(sidereal)
                }

        # SIMPLE & STABLE LAGNA (demo-grade)
        lagna_deg = (t.sidereal_time('mean', lon*u.deg).degree) % 360

        result = {
            "lagna": {
                "degree": round(lagna_deg,2),
                "rashi": degree_to_rashi(lagna_deg)
            },
            "positions": positions,
            "dasha": vimshottari_dasha(positions['moon']['degree'])
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
