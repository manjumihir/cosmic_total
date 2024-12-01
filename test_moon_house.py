from utils.astro_calc import AstroCalc
from datetime import datetime
import pytz

def test_moon_house():
    # Create an instance
    calc = AstroCalc()
    
    # Set birth data
    tz = pytz.timezone("Asia/Kolkata")
    birth_dt = tz.localize(datetime(1969, 12, 20, 22, 55, 0))
    
    # Calculate chart
    chart = calc.calculate_chart(birth_dt, 13.0827, 80.2707)
    
    # Get Moon's details
    moon_details = chart["points"]["Moon"]
    moon_long = moon_details["longitude"]
    moon_house = moon_details["house"]
    
    print("\nMoon Details:")
    print(f"Moon longitude: {moon_long:.2f}°")
    print(f"Moon sign: {moon_details['sign']}")
    print(f"Moon house: {moon_house}")
    
    # Print house cusps and check which house the Moon should be in
    print("\nHouse Cusps and Moon Placement:")
    for i in range(1, 13):
        house = chart["houses"][f"House_{i}"]
        cusp = house["longitude"]
        next_cusp = chart["houses"][f"House_{(i % 12) + 1}"]["longitude"] if i < 12 else chart["houses"]["House_1"]["longitude"]
        print(f"House {i}: {cusp:.2f}° ({house['sign']})")
        
        # Check if Moon is in this house
        if cusp > next_cusp:  # House spans 0° Aries
            if moon_long >= cusp or moon_long < next_cusp:
                print(f">>> Moon at {moon_long:.2f}° should be in house {i} (spans 0° Aries)")
        else:  # Regular house
            if cusp <= moon_long < next_cusp:
                print(f">>> Moon at {moon_long:.2f}° should be in house {i}")

if __name__ == "__main__":
    test_moon_house()
