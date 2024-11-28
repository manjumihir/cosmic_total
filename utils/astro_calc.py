import swisseph as swe
from datetime import datetime, timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta

class AstroCalc:
    def __init__(self):
        # Initialize ephemeris path - update this path
        swe.set_ephe_path('./ephe')
        
        self.signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                     "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        self.house_system_map = {
            "Placidus": b'P',
            "Koch": b'K',
            "Equal (Asc)": b'E',
            "Equal (MC)": b'X',
            "Whole Sign": b'W',
            "Campanus": b'C',
            "Regiomontanus": b'R',
            "Porphyry": b'O',
            "Morinus": b'M',
            "Meridian": b'A',
            "Alcabitius": b'B',
            "Azimuthal": b'H',
            "Polich/Page (Topocentric)": b'T',
            "Vehlow Equal": b'V'
        }
        
        self.ayanamsa_map = {
            "Lahiri": swe.SIDM_LAHIRI,
            "Raman": swe.SIDM_RAMAN,
            "Krishnamurti": swe.SIDM_KRISHNAMURTI,
            "Fagan/Bradley": swe.SIDM_FAGAN_BRADLEY,
            "True Chitrapaksha": swe.SIDM_TRUE_CITRA
        }
        
        # Add node calculation type
        self.node_type = "True"  # Default to True Nodes
        
        # Update planets dictionary to include nodes
        self.planets = {
            swe.SUN: "Sun",
            swe.MOON: "Moon",
            swe.MERCURY: "Mercury",
            swe.VENUS: "Venus",
            swe.MARS: "Mars",
            swe.JUPITER: "Jupiter",
            swe.SATURN: "Saturn",
            swe.URANUS: "Uranus",
            swe.NEPTUNE: "Neptune",
            swe.PLUTO: "Pluto",
            swe.TRUE_NODE if self.node_type == "True" else swe.MEAN_NODE: "Rahu"
        }

        # Add Nakshatra data
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        # Nakshatra Lords (in order)
        self.nakshatra_lords = [
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
            "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
            "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
            "Jupiter", "Saturn", "Mercury"
        ]
        
        # Sub-division lords (for Vimsottari dasha)
        self.sub_lords = {
            "Ketu": ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"],
            "Venus": ["Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu"],
            "Sun": ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"],
            "Moon": ["Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun"],
            "Mars": ["Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon"],
            "Rahu": ["Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars"],
            "Jupiter": ["Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu"],
            "Saturn": ["Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter"],
            "Mercury": ["Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn"]
        }

    def datetime_to_julian(self, dt):
        """Convert datetime to Julian Day."""
        try:
            # Adjust for India timezone (UTC+5:30)
            utc_dt = dt - timedelta(hours=5, minutes=30)
            
            print("\nTime Conversion Details:")
            print(f"Input local time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Converted UTC time: {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Convert to Julian Day
            jd = swe.julday(utc_dt.year, 
                           utc_dt.month,
                           utc_dt.day,
                           utc_dt.hour + 
                           utc_dt.minute/60.0 + 
                           utc_dt.second/3600.0)
            
            print(f"Calculated Julian Day: {jd}")
            return jd
        except Exception as e:
            print(f"Error in datetime_to_julian: {e}")
            raise

    def get_nakshatra_data(self, longitude):
        """Calculate nakshatra, pada, and lords for a given longitude."""
        nakshatra_length = 13.333333  # 360/27
        pada_length = nakshatra_length / 4

        # Calculate nakshatra number (0-26)
        nakshatra_num = int(longitude / nakshatra_length)
        
        # Calculate pada (1-4)
        pada = int((longitude % nakshatra_length) / pada_length) + 1
        
        # Get star lord (nakshatra lord)
        star_lord = self.nakshatra_lords[nakshatra_num]
        
        # Calculate sub-lord
        position_in_nakshatra = (longitude % nakshatra_length) / nakshatra_length
        sub_division = position_in_nakshatra * 9  # 9 sub-divisions
        sub_lord_index = int(sub_division)
        sub_lord = self.sub_lords[star_lord][sub_lord_index]

        return {
            "nakshatra": self.nakshatras[nakshatra_num],
            "pada": pada,
            "star_lord": star_lord,
            "sub_lord": sub_lord
        }

    def calculate_chart(self, dt, lat, lon, calc_type="Topocentric", 
                       zodiac="Sidereal", ayanamsa="Lahiri", 
                       house_system="Placidus", node_type="True Node (Rahu/Ketu)"):
        """Calculate full birth chart."""
        try:
            # Strip out the (Rahu/Ketu) part for the calculation
            node_type_base = node_type.split(" (")[0]  # This will give "True Node" or "Mean Node"
            
            # Set the appropriate flag for node calculation
            node_flag = swe.FLG_SWIEPH
            if node_type_base == "Mean Node":
                rahu_id = swe.MEAN_NODE
                ketu_id = swe.MEAN_NODE
            else:  # "True Node"
                rahu_id = swe.TRUE_NODE
                ketu_id = swe.TRUE_NODE

            # Update node type
            self.node_type = node_type
            
            # Convert to Julian Day
            julian_day = self.datetime_to_julian(dt)
            
            # Set calculation flags
            flags = 0
            
            # Handle Topocentric setting
            if calc_type == "Topocentric":
                flags |= swe.FLG_TOPOCTR
                swe.set_topo(float(lat), float(lon), 0)
            
            # Handle Sidereal setting
            if zodiac == "Sidereal":
                flags |= swe.FLG_SIDEREAL
                swe.set_sid_mode(self.ayanamsa_map[ayanamsa])
            
            # Get ayanamsa value
            ayanamsa_value = swe.get_ayanamsa(julian_day)
            
            # Calculate houses
            house_system_code = self.house_system_map[house_system]
            houses_data = swe.houses_ex(julian_day, float(lat), float(lon), house_system_code)
            
            # Get ascendant
            tropical_asc = houses_data[1][0]
            sidereal_asc = tropical_asc - ayanamsa_value if zodiac == "Sidereal" else tropical_asc
            
            # Normalize to 0-360 range
            if sidereal_asc < 0:
                sidereal_asc += 360
            elif sidereal_asc >= 360:
                sidereal_asc -= 360
            
            # Initialize results
            results = {
                "meta": {
                    "datetime": dt.strftime('%Y-%m-%d %H:%M:%S'),
                    "latitude": lat,
                    "longitude": lon,
                    "calculation_type": calc_type,
                    "zodiac_system": zodiac,
                    "ayanamsa": ayanamsa,
                    "ayanamsa_value": ayanamsa_value,
                    "house_system": house_system
                },
                "points": {},
                "houses": {}
            }
            
            # Add ascendant
            asc_sign_num = int(sidereal_asc / 30)
            results["points"]["Ascendant"] = {
                'longitude': sidereal_asc,
                'sign': self.signs[asc_sign_num],
                'house': 1,
                'degree': sidereal_asc % 30
            }
            
            # Calculate planets
            for planet_id, planet_name in self.planets.items():
                calc = swe.calc(julian_day, planet_id, flags)
                longitude = calc[0][0]
                
                # Get nakshatra data
                nakshatra_data = self.get_nakshatra_data(longitude)
                
                results["points"][planet_name] = {
                    'longitude': longitude,
                    'sign': self.signs[int(longitude / 30)],
                    'house': self.determine_house(longitude, houses_data[0]),
                    'is_retrograde': calc[0][3] < 0,
                    'degree': longitude % 30,
                    'nakshatra': nakshatra_data['nakshatra'],
                    'pada': nakshatra_data['pada'],
                    'star_lord': nakshatra_data['star_lord'],
                    'sub_lord': nakshatra_data['sub_lord']
                }
            
            # Calculate Rahu (North Node)
            rahu_calc = swe.calc(julian_day, rahu_id, flags)
            rahu_longitude = rahu_calc[0][0]
            rahu_sign_num = int(rahu_longitude / 30)
            rahu_house = self.determine_house(rahu_longitude, houses_data[0])
            
            # Calculate Ketu (South Node) - always 180° opposite to Rahu
            ketu_longitude = (rahu_longitude + 180) % 360
            ketu_sign_num = int(ketu_longitude / 30)
            ketu_house = self.determine_house(ketu_longitude, houses_data[0])
            
            # Add nodes to results
            results["points"]["Rahu"] = {
                'longitude': rahu_longitude,
                'sign': self.signs[rahu_sign_num],
                'house': rahu_house,
                'degree': rahu_longitude % 30,
                'type': f"{node_type} Node"
            }
            
            results["points"]["Ketu"] = {
                'longitude': ketu_longitude,
                'sign': self.signs[ketu_sign_num],
                'house': ketu_house,
                'degree': ketu_longitude % 30,
                'type': f"{node_type} Node"
            }

            # Special handling for Rahu and Ketu
            rahu_longitude = results["points"]["Rahu"]["longitude"]
            ketu_longitude = results["points"]["Ketu"]["longitude"]
            
            # Add nakshatra data for Rahu
            rahu_nakshatra = self.get_nakshatra_data(rahu_longitude)
            results["points"]["Rahu"].update({
                "nakshatra": rahu_nakshatra["nakshatra"],
                "pada": rahu_nakshatra["pada"],
                "star_lord": rahu_nakshatra["star_lord"],
                "sub_lord": rahu_nakshatra["sub_lord"],
                "type": "True Node"
            })
            
            # Add nakshatra data for Ketu
            ketu_nakshatra = self.get_nakshatra_data(ketu_longitude)
            results["points"]["Ketu"].update({
                "nakshatra": ketu_nakshatra["nakshatra"],
                "pada": ketu_nakshatra["pada"],
                "star_lord": ketu_nakshatra["star_lord"],
                "sub_lord": ketu_nakshatra["sub_lord"],
                "type": "True Node"
            })

            # Add house calculations with nakshatra details
            for house in range(1, 13):
                cusp_longitude = houses_data[0][house - 1]
                if zodiac == "Sidereal":
                    cusp_longitude -= ayanamsa_value
                    if cusp_longitude < 0:
                        cusp_longitude += 360
                
                # Get nakshatra data for house cusp
                nakshatra_data = self.get_nakshatra_data(cusp_longitude)
                
                results["houses"][f"House_{house}"] = {
                    "longitude": cusp_longitude,
                    "sign": self.signs[int(cusp_longitude / 30)],
                    "degree": cusp_longitude % 30,
                    "nakshatra": nakshatra_data['nakshatra'],
                    "pada": nakshatra_data['pada'],
                    "star_lord": nakshatra_data['star_lord'],
                    "sub_lord": nakshatra_data['sub_lord']
                }

            return results
                
        except Exception as e:
            print(f"Error in calculate_chart: {e}")
            raise

    def determine_house(self, longitude, house_cusps):
        """Helper function to determine house placement."""
        for i in range(12):
            next_cusp = house_cusps[(i + 1) % 12]
            current_cusp = house_cusps[i]
            
            # Handle case where house spans 0° Aries
            if current_cusp > next_cusp:
                if longitude >= current_cusp or longitude < next_cusp:
                    return i + 1
            else:
                if current_cusp <= longitude < next_cusp:
                    return i + 1
        return 1  # Default to 1st house if no match found 

class DashaCalculator:
    def __init__(self):
        # Dasha order and durations (in years)
        self.dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        self.dasha_years = {
            "Ketu": 7, 
            "Venus": 20, 
            "Sun": 6, 
            "Moon": 10, 
            "Mars": 7, 
            "Rahu": 18, 
            "Jupiter": 16, 
            "Saturn": 19, 
            "Mercury": 17
        }

    def calculate_period(self, total_minutes):
        """Convert total minutes to years, months, days, hours, minutes"""
        years = total_minutes // (525600)  # 365.25 * 24 * 60
        remaining_minutes = total_minutes % 525600
        
        months = remaining_minutes // 43800  # 30.4167 * 24 * 60
        remaining_minutes = remaining_minutes % 43800
        
        days = remaining_minutes // 1440  # 24 * 60
        remaining_minutes = remaining_minutes % 1440
        
        hours = remaining_minutes // 60
        minutes = remaining_minutes % 60
        
        return years, months, days, hours, minutes

    def format_duration(self, years, months, days, hours, minutes):
        """Format duration string with all components"""
        parts = []
        if years > 0:
            parts.append(f"{years}y")
        if months > 0:
            parts.append(f"{months}m")
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}min")
        return " ".join(parts) if parts else "0min"

    def add_period_to_datetime(self, dt, total_minutes):
        """Add exact minutes to a datetime"""
        return dt + timedelta(minutes=total_minutes)

    def calculate_dashas(self, birth_date, moon_longitude):
        """Calculate all five levels of dashas"""
        try:
            nakshatra_degree = moon_longitude % 13.333333
            balance = 1 - (nakshatra_degree / 13.333333)
            nakshatra_number = int(moon_longitude / 13.333333)
            start_lord_index = nakshatra_number % 9

            all_dashas = []
            current_date = birth_date

            # Mahadasha calculation
            for i in range(9):
                lord_index = (start_lord_index + i) % 9
                lord = self.dasha_order[lord_index]
                total_minutes = self.dasha_years[lord] * 525600  # Convert years to minutes

                if i == 0:
                    total_minutes = int(total_minutes * balance)

                end_date = self.add_period_to_datetime(current_date, total_minutes)
                years, months, days, hours, mins = self.calculate_period(total_minutes)
                duration_str = self.format_duration(years, months, days, hours, mins)

                maha_dasha = {
                    'lord': lord,
                    'start_date': current_date,
                    'end_date': end_date,
                    'duration_str': duration_str,
                    'sub_dashas': self.calculate_antardashas(current_date, total_minutes, lord)
                }

                all_dashas.append(maha_dasha)
                current_date = end_date

            return all_dashas

        except Exception as e:
            print(f"Error in calculate_dashas: {e}")
            raise

    def calculate_antardashas(self, start_date, total_minutes, main_lord):
        """Calculate Antardashas (level 2)"""
        antardashas = []
        current_date = start_date
        start_index = self.dasha_order.index(main_lord)

        for i in range(9):
            lord_index = (start_index + i) % 9
            antardasha_lord = self.dasha_order[lord_index]
            antardasha_minutes = (total_minutes * self.dasha_years[antardasha_lord]) // 120

            end_date = self.add_period_to_datetime(current_date, antardasha_minutes)
            years, months, days, hours, mins = self.calculate_period(antardasha_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            antardasha = {
                'lord': f"{main_lord}-{antardasha_lord}",
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str,
                'sub_dashas': self.calculate_pratyantar_dashas(current_date, antardasha_minutes, 
                                                             main_lord, antardasha_lord)
            }

            antardashas.append(antardasha)
            current_date = end_date

        return antardashas

    def calculate_pratyantar_dashas(self, start_date, total_minutes, main_lord, antardasha_lord):
        """Calculate Pratyantar dashas (level 3)"""
        pratyantars = []
        current_date = start_date
        start_index = self.dasha_order.index(antardasha_lord)

        for i in range(9):
            lord_index = (start_index + i) % 9
            pratyantar_lord = self.dasha_order[lord_index]
            pratyantar_minutes = (total_minutes * self.dasha_years[pratyantar_lord]) // 120

            end_date = self.add_period_to_datetime(current_date, pratyantar_minutes)
            years, months, days, hours, mins = self.calculate_period(pratyantar_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            pratyantar = {
                'lord': f"{main_lord}-{antardasha_lord}-{pratyantar_lord}",
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str,
                'sub_dashas': self.calculate_sookshma_dashas(current_date, pratyantar_minutes,
                                                           main_lord, antardasha_lord, pratyantar_lord)
            }

            pratyantars.append(pratyantar)
            current_date = end_date

        return pratyantars

    def calculate_sookshma_dashas(self, start_date, total_minutes, main_lord, antardasha_lord, pratyantar_lord):
        """Calculate Sookshma dashas (level 4)"""
        sookshmas = []
        current_date = start_date
        start_index = self.dasha_order.index(pratyantar_lord)

        for i in range(9):
            lord_index = (start_index + i) % 9
            sookshma_lord = self.dasha_order[lord_index]
            sookshma_minutes = (total_minutes * self.dasha_years[sookshma_lord]) // 120

            end_date = self.add_period_to_datetime(current_date, sookshma_minutes)
            years, months, days, hours, mins = self.calculate_period(sookshma_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            sookshma = {
                'lord': f"{main_lord}-{antardasha_lord}-{pratyantar_lord}-{sookshma_lord}",
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str,
                'sub_dashas': self.calculate_prana_dashas(current_date, sookshma_minutes,
                                                        main_lord, antardasha_lord, pratyantar_lord, sookshma_lord)
            }

            sookshmas.append(sookshma)
            current_date = end_date

        return sookshmas

    def calculate_prana_dashas(self, start_date, total_minutes, main_lord, antardasha_lord, 
                             pratyantar_lord, sookshma_lord):
        """Calculate Prana dashas (level 5)"""
        pranas = []
        current_date = start_date
        start_index = self.dasha_order.index(sookshma_lord)

        for i in range(9):
            lord_index = (start_index + i) % 9
            prana_lord = self.dasha_order[lord_index]
            prana_minutes = (total_minutes * self.dasha_years[prana_lord]) // 120

            end_date = self.add_period_to_datetime(current_date, prana_minutes)
            years, months, days, hours, mins = self.calculate_period(prana_minutes)
            duration_str = self.format_duration(years, months, days, hours, mins)

            prana = {
                'lord': f"{main_lord}-{antardasha_lord}-{pratyantar_lord}-{sookshma_lord}-{prana_lord}",
                'start_date': current_date,
                'end_date': end_date,
                'duration_str': duration_str
            }

            pranas.append(prana)
            current_date = end_date

        return pranas