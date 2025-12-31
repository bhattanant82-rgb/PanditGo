from flask import Flask, request, jsonify
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, get_body, EarthLocation, GCRS
import astropy.units as u
from datetime import datetime

app = Flask(__name__)

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