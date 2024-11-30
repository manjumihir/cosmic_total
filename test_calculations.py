from kerykeion import AstrologicalSubject, Report
from utils.astro_calc import AstroCalc
from datetime import datetime
import swisseph as swe
from datetime import timedelta

# Test data
test_date = datetime(1990, 1, 1, 12, 0)  # January 1, 1990, 12:00
test_lat = 12.9716  # Bangalore latitude
test_lon = 77.5946  # Bangalore longitude

def normalize_degrees(deg):
    """Convert absolute degrees to sign-relative degrees and sign number"""
    sign_num = int(deg / 30)
    rel_deg = deg % 30
    return sign_num, rel_deg

def print_position(title, deg):
    sign_num, rel_deg = normalize_degrees(deg)
    signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    print(f"{title}:")
    print(f"  Absolute: {deg}°")
    print(f"  Sign: {signs[sign_num]} ({sign_num})")
    print(f"  Relative: {rel_deg}°")

def print_detailed_calc(title, jd, lat, lon, ayanamsa):
    print(f"\n=== {title} ===")
    print(f"Julian Day: {jd}")
    print(f"Ayanamsa: {ayanamsa}")
    
    # Get raw house data
    houses = swe.houses_ex(jd, lat, lon, b'P')
    print(f"Raw Ascendant (Tropical): {houses[1][0]}")
    
    # Calculate sidereal position
    sid_asc = houses[1][0] - ayanamsa
    if sid_asc < 0:
        sid_asc += 360
    print_position("Sidereal Ascendant", sid_asc)

# Kerykeion calculation
print("=== Kerykeion Calculation ===")
k = AstrologicalSubject(
    name="Test",
    year=test_date.year,
    month=test_date.month,
    day=test_date.day,
    hour=test_date.hour,
    minute=test_date.minute,
    lat=test_lat,
    lng=test_lon,
    city="Bangalore",
    nation="IN",
    tz_str="Asia/Kolkata",
    zodiac_type="Sidereal",
    sidereal_mode="LAHIRI",
    houses_system_identifier="P",  # Placidus
    perspective_type="Topocentric",
    online=False
)

print(f"\nTime Details:")
print(f"Julian Day: {k.julian_day}")
print(f"UTC Time: {k.iso_formatted_utc_datetime}")
print(f"Local Time: {k.iso_formatted_local_datetime}")

# Convert Kerykeion's position to absolute degrees
ker_sign_num = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", 
                "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"].index(k.first_house.sign)
ker_abs_deg = ker_sign_num * 30 + k.first_house.position

print("\nKerykeion Ascendant:")
print_position("Kerykeion Format", k.first_house.position)
print_position("Absolute Format", ker_abs_deg)

# Your calculation
print("\n=== Your Calculation ===")
ac = AstroCalc()
chart = ac.calculate_chart(
    dt=test_date,
    lat=test_lat,
    lon=test_lon,
    calc_type="Topocentric",
    zodiac="Sidereal",
    ayanamsa="Lahiri",
    house_system="Placidus"
)

asc = chart["points"]["Ascendant"]
print("\nYour Ascendant:")
print_position("Your Format", asc['longitude'])

# Direct Swiss Ephemeris calculation
print("\n=== Direct Swiss Ephemeris ===")
utc_dt = test_date - timedelta(hours=5, minutes=30)
jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)

swe.set_sid_mode(swe.SIDM_LAHIRI)
ayanamsa = swe.get_ayanamsa(jd)
houses = swe.houses_ex(jd, test_lat, test_lon, b'P')
sid_asc = houses[1][0] - ayanamsa
if sid_asc < 0:
    sid_asc += 360

print("\nSwiss Ephemeris Ascendant:")
print_position("Direct Calculation", sid_asc)

# Try with different time handling
print("\n=== Alternative Time Handling ===")
# Use local time directly
local_jd = swe.julday(test_date.year, test_date.month, test_date.day,
                      test_date.hour + test_date.minute/60.0)
print_detailed_calc("Local Time Direct", local_jd, test_lat, test_lon, ayanamsa)
