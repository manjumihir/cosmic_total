from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QMessageBox)
from datetime import datetime

class YogeswarananadaWindow(QDialog):
    def __init__(self, chart_data, parent=None):
        super().__init__(parent)
        self.chart_data = chart_data
        self.house_points = {i: 0 for i in range(1, 13)}  # Initialize points for each house
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("yogeswarananada_12 Calculations")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        output = self.calculate_yogeswarananada()
        self.results_text.setText(output)
        
        layout.addWidget(self.results_text)
        self.setLayout(layout)

    def get_house_lord(self, sign):
        """Get the lord of a sign"""
        sign_lords = {
            'Aries': 'Mars',
            'Taurus': 'Venus',
            'Gemini': 'Mercury',
            'Cancer': 'Moon',
            'Leo': 'Sun',
            'Virgo': 'Mercury',
            'Libra': 'Venus',
            'Scorpio': 'Mars',
            'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn',
            'Aquarius': 'Saturn',
            'Pisces': 'Jupiter'
        }
        return sign_lords.get(sign)

    def get_houses_owned_by(self, planet):
        """Get list of houses owned by a planet"""
        owned_houses = []
        for house_num in range(1, 13):
            house_key = f"House_{house_num}"
            house_sign = self.chart_data['houses'][house_key]['sign']
            if self.get_house_lord(house_sign) == planet:
                owned_houses.append(house_num)
        return owned_houses

    def add_points(self, house_num, points, reason=""):
        """Add points to a house and track the reason"""
        self.house_points[house_num] += points
        return f"House {house_num}: +{points} points ({reason})\n"

    def handle_rahu_ketu(self, planet, house_num, points, point_type):
        """Special handling for Rahu/Ketu points"""
        details = ""
        if planet in ['Rahu', 'Ketu']:
            house_sign = self.chart_data['houses'][f"House_{house_num}"]['sign']
            house_lord = self.get_house_lord(house_sign)
            
            # Give points to houses owned by the house lord
            for owned_house in self.get_houses_owned_by(house_lord):
                details += self.add_points(owned_house, points, 
                    f"{point_type} points via {planet}'s house lord {house_lord}")
            
            # Extra point for house lord's placement
            lord_house = None
            for h in range(1, 13):
                if self.chart_data['points'][house_lord]['house'] == h:
                    lord_house = h
                    break
            if lord_house:
                details += self.add_points(lord_house, 1, 
                    f"Extra point for {house_lord}'s placement (as {planet}'s house lord)")
        
        return details

    def get_current_dasa_lord(self):
        """Determine the current dasa lord from chart data"""
        try:
            # First try to get from dashas if available
            if 'dashas' in self.chart_data:
                current_time = datetime.now()
                for dasha in self.chart_data['dashas']:
                    start_date = dasha['start_date']
                    end_date = dasha['end_date']
                    if start_date <= current_time <= end_date:
                        return dasha['lord']
            
            # If no dashas data, calculate using moon's position
            moon_longitude = self.chart_data['points']['Moon']['longitude']
            birth_date = datetime.strptime(self.chart_data['meta']['datetime'], '%Y-%m-%d %H:%M:%S')
            
            from utils.astro_calc import DashaCalculator
            dasha_calc = DashaCalculator()
            all_dashas = dasha_calc.calculate_dashas(birth_date, moon_longitude)
            
            current_time = datetime.now()
            for dasha in all_dashas:
                if dasha['start_date'] <= current_time <= dasha['end_date']:
                    return dasha['lord']
            
            print("Warning: Could not determine current dasa lord")
            return 'Moon'  # Fallback
            
        except Exception as e:
            print(f"Error determining dasa lord: {e}")
            return 'Moon'  # Fallback

    def calculate_house_strengths(self, x, y, z):
        """Calculate house strengths for given X, Y, Z planets"""
        output = "Point Distribution Details:\n"
        output += "-------------------------\n"
        
        # Handle X (Main Planet)
        x_data = self.chart_data['points'][x]
        if x in ['Rahu', 'Ketu']:
            output += self.handle_rahu_ketu(x, x_data['house'], 1, "Power 1: Main Planet")
        else:
            # Power 1: Houses owned by X
            for house in self.get_houses_owned_by(x):
                output += self.add_points(house, 1, f"Power 1: House owned by {x}")
        # Power 2: House where X is placed
        output += self.add_points(x_data['house'], 2, f"Power 2: House where {x} is placed")
        
        # Handle Y (Star Lord) - only if different from X
        if y != x:
            y_data = self.chart_data['points'][y]
            if y in ['Rahu', 'Ketu']:
                output += self.handle_rahu_ketu(y, y_data['house'], 3, "Power 3: Star Lord")
            else:
                # Power 3: Houses owned by Y
                for house in self.get_houses_owned_by(y):
                    output += self.add_points(house, 3, f"Power 3: House owned by {y}")
            # Power 4: House where Y is placed
            output += self.add_points(y_data['house'], 4, f"Power 4: House where {y} is placed")
        
        # Handle Z (Sub Lord)
        z_data = self.chart_data['points'][z]
        if z in ['Rahu', 'Ketu']:
            output += self.handle_rahu_ketu(z, z_data['house'], 5, "Power 5: Sub Lord")
        else:
            # Power 5: Houses owned by Z
            for house in self.get_houses_owned_by(z):
                output += self.add_points(house, 5, f"Power 5: House owned by {z}")
        # Power 6: House where Z is placed
        output += self.add_points(z_data['house'], 6, f"Power 6: House where {z} is placed")
        
        # Handle cuspal points
        for house_num in range(1, 13):
            house_data = self.chart_data['houses'][f"House_{house_num}"]
            
            # Powers 7 & 10: X as cuspal lord
            if house_data['star_lord'] == x:
                output += self.add_points(house_num, 7, f"Power 7: House where {x} is star lord of cusp")
            if house_data['sub_lord'] == x:
                output += self.add_points(house_num, 10, f"Power 10: House where {x} is sub lord of cusp")
            
            # Powers 8 & 11: Y as cuspal lord (only if different from X)
            if y != x:
                if house_data['star_lord'] == y:
                    output += self.add_points(house_num, 8, f"Power 8: House where {y} is star lord of cusp")
                if house_data['sub_lord'] == y:
                    output += self.add_points(house_num, 11, f"Power 11: House where {y} is sub lord of cusp")
            
            # Powers 9 & 12: Z as cuspal lord
            if house_data['star_lord'] == z:
                output += self.add_points(house_num, 9, f"Power 9: House where {z} is star lord of cusp")
            if house_data['sub_lord'] == z:
                output += self.add_points(house_num, 12, f"Power 12: House where {z} is sub lord of cusp")
        
        return output

    def calculate_single_planet(self, planet, role):
        """Helper method to calculate for a single planet"""
        x_data = self.chart_data['points'][planet]
        y = x_data['star_lord']
        z = x_data['sub_lord']
        
        details = f"Planets Involved:\n"
        details += f"{role} (X): {planet}\n"
        details += f"Star Lord (Y): {y}\n"
        details += f"Sub Lord (Z): {z}\n\n"
        
        details += self.calculate_house_strengths(planet, y, z)
        details += "\nResults:\n"
        for house, points in self.house_points.items():
            details += f"House {house}: {points} points\n"
        
        return details

    def calculate_yogeswarananada(self):
        try:
            output = "Yogeswarananada House Strength Calculations\n"
            output += "=========================================\n\n"
            
            calculated_results = {}
            
            # Start with Moon calculations
            moon_data = self.chart_data['points']['Moon']
            moon_star_lord = moon_data['star_lord']
            moon_sub_lord = moon_data['sub_lord']
            
            # 1. Moon calculation
            output += "1. Moon - " + moon_star_lord + " - " + moon_sub_lord + "\n"
            output += "=" * 40 + "\n"
            self.house_points = {i: 0 for i in range(1, 13)}
            details = self.calculate_single_planet('Moon', "X")
            output += details
            calculated_results['Moon'] = True

            # 2. Moon's star lord calculation
            star_lord_data = self.chart_data['points'][moon_star_lord]
            star_lord_star = star_lord_data['star_lord']
            star_lord_sub = star_lord_data['sub_lord']
            
            output += f"\n2. {moon_star_lord} - {star_lord_star} - {star_lord_sub}\n"
            output += "=" * 40 + "\n"
            self.house_points = {i: 0 for i in range(1, 13)}
            details = self.calculate_single_planet(moon_star_lord, "X")
            output += details
            calculated_results[moon_star_lord] = True

            # Calculate for remaining planets
            all_planets = ['Sun', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
            count = 3

            for planet in all_planets:
                if planet not in calculated_results:
                    planet_data = self.chart_data['points'][planet]
                    output += f"\n{count}. {planet} - {planet_data['star_lord']} - {planet_data['sub_lord']}\n"
                    output += "=" * 40 + "\n"
                    self.house_points = {i: 0 for i in range(1, 13)}
                    details = self.calculate_single_planet(planet, "X")
                    output += details
                    calculated_results[planet] = True
                    count += 1

            return output
            
        except Exception as e:
            import traceback
            return f"Error in calculations: {str(e)}\n{traceback.format_exc()}"