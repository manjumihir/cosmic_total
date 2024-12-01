from utils.astro_calc import AstroCalc
from datetime import datetime

def print_chart_details(chart):
    """Print detailed chart information"""
    print("\nChart Details:")
    print("-------------")
    
    # Print ascendant
    asc_data = chart['houses']['House_1']
    print(f"\nAscendant: {asc_data['longitude']:.2f}° ({asc_data['sign']})")
    
    # Print all planets
    print("\nPlanet Positions:")
    for planet, data in chart['points'].items():
        print(f"{planet:8} : {data['longitude']:6.2f}° ({data['sign']:12}) House {data['house']}")
    
    # Print all house cusps
    print("\nHouse Cusps:")
    for i in range(1, 13):
        house_data = chart['houses'][f'House_{i}']
        print(f"House {i:2} : {house_data['longitude']:6.2f}° ({house_data['sign']:12})")

# Initialize calculator
calc = AstroCalc()

# Mihir1 birth details
birth_dt = datetime.strptime("20/12/1969 22:55", "%d/%m/%Y %H:%M")
lat = 20.233333333333334  # 20° 14' 00" N
lon = 85.83333333333333   # 85° 50' 00" E

# Calculate chart
chart = calc.calculate_chart(
    birth_dt, 
    lat, 
    lon,
    calc_type="Topocentric",
    zodiac="Sidereal",
    ayanamsa="Lahiri",
    house_system="Placidus"
)

# Print full chart details
print_chart_details(chart)
