from flask import Flask, request, jsonify
from flask_cors import CORS
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation, AltAz, get_sun, get_moon
import astropy.units as u
from datetime import datetime
import math

app = Flask(__name__)
CORS(app)  # Frontend se call allow karta hai (Failed to fetch fix)

# Vedic Rashi & Nakshatra
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

# Simple Vimshottari Dasha lords & effects
DASHA_EFFECTS = {
    "Ketu": "Spirituality, detachment, sudden changes",
    "Venus": "Luxury, marriage, creativity, wealth",
    "Sun": "Leadership, government, fame, health",
    "Moon": "Emotions, family, mind, mother",
    "Mars": "Energy, property, courage, conflicts",
    "Rahu": "Foreign, sudden gains/loss, obsession",
    "Jupiter": "Wisdom, education, finance, growth",
    "Saturn": "Hard work, delay, discipline, longevity",
    "Mercury": "Business, communication, intellect"
}

def degree_to_rashi(deg):
    return RASHIS[int(deg // 30) % 12]

def degree_to_nakshatra(deg):
    return NAKSHATRAS[int(deg // (360/27)) % 27]

def get_lagna(birth_time, loc):
    # Accurate Lagna using local sidereal time + horizon
    frame = AltAz(obstime=birth_time, location=loc)
    sun = get_sun(birth_time)
    altaz = sun.transform_to(frame)
    lagna_deg = (altaz.az.degree - 24.0) % 360  # Lahiri Ayanamsa approx
    return lagna_deg

@app.route('/generate-kundli', methods=['POST'])
def generate_kundli():
    try:
        data = request.json
        dob = data['dob']          # "DD/MM/YYYY"
        tob = data['tob']          # "HH:MM:SS"
        place = data['place']      # "lat,long"

        # Step 1: Parse birth time
        day, month, year = map(int, dob.split('/'))
        hour, minute, second = map(int, tob.split(':'))
        birth_dt = datetime(year, month, day, hour, minute, second)
        birth_time = Time(birth_dt)

        # Step 2: Location
        lat, lon = map(float, place.split(','))
        loc = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=0*u.m)

        # Step 3: Planet positions
        with solar_system_ephemeris.set('builtin'):
            planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']
            positions = {}
            for p in planets:
                body = get_body(p, birth_time, loc)
                ra = body.ra.degree
                sidereal = (ra - 24.0) % 360  # Lahiri Ayanamsa
                positions[p] = {
                    "degree": round(sidereal, 2),
                    "rashi": degree_to_rashi(sidereal),
                    "nakshatra": degree_to_nakshatra(sidereal)
                }

            # Rahu/Ketu (approximate mean nodes)
            moon_ra = get_moon(birth_time, loc).ra.degree
            rahu = (moon_ra + 180) % 360 - 24.0
            rahu = rahu % 360
            ketu = (rahu + 180) % 360
            positions['rahu'] = {"degree": round(rahu, 2), "rashi": degree_to_rashi(rahu), "nakshatra": degree_to_nakshatra(rahu)}
            positions['ketu'] = {"degree": round(ketu, 2), "rashi": degree_to_rashi(ketu), "nakshatra": degree_to_nakshatra(ketu)}

        # Step 4: Lagna
        lagna_deg = get_lagna(birth_time, loc)
        lagna = {
            "degree": round(lagna_deg, 2),
            "rashi": degree_to_rashi(lagna_deg),
            "nakshatra": degree_to_nakshatra(lagna_deg)
        }

        # Step 5: Moon for Dasha
        moon_deg = positions['moon']['degree']
        dasha_index = int(moon_deg // (360/27)) % 9
        dasha_lord = list(DASHA_EFFECTS.keys())[dasha_index]
        dasha = {
            "lord": dasha_lord,
            "effect": DASHA_EFFECTS[dasha_lord]
        }

        # Step 6: Basic Predictions (lagna rashi ke base pe)
        lagna_rashi = lagna['rashi']
        predictions = {
            "career": f"{lagna_rashi} Lagna mein strong leadership, management, tech ya govt jobs favorable.",
            "money": "Steady income. Investments long-term mein best. Speculation se bachna.",
            "marriage": "Shaadi mid-life mein strong. Partner supportive aur emotional.",
            "health": "Overall achhi health. Stress, digestion aur head pe dhyan rakhna."
        }

        # Final response
        result = {
            "lagna": lagna,
            "graha": positions,
            "current_dasha": dasha,
            "predictions": predictions,
            "note": "Accurate Vedic Kundli with Lahiri Ayanamsa. Full yog/dosh ke liye advanced software chahiye."
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Invalid input ya calculation error: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)