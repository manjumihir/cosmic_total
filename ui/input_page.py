import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                           QPushButton, QLabel, QMessageBox, QDialog, 
                           QTableWidget, QTableWidgetItem, QTextEdit, 
                           QGroupBox, QComboBox, QScrollArea, QDateTimeEdit,
                           QTreeWidget, QTreeWidgetItem, QStackedWidget, QApplication)
from PyQt6.QtCore import QDateTime, Qt
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import json
from utils.astro_calc import AstroCalc, DashaCalculator
from datetime import datetime
from PyQt6 import QtGui
from .yogeswarananada_window import YogeswarananadaWindow
from .chart_widgets import NorthernChartWidget
from .chart_dialog import ChartDialog

class InputPage(QWidget):
    def __init__(self):
        super().__init__()
        self.astro_calc = AstroCalc()
        self.chart_data = None
        self.init_ui()
        
    def decimal_to_dms(self, decimal, is_latitude=True):
        """Convert decimal degrees to degrees, minutes, seconds string"""
        direction = ""
        if is_latitude:
            direction = "N" if decimal >= 0 else "S"
        else:
            direction = "E" if decimal >= 0 else "W"
        
        decimal = abs(decimal)
        degrees = int(decimal)
        decimal_minutes = (decimal - degrees) * 60
        minutes = int(decimal_minutes)
        decimal_seconds = (decimal_minutes - minutes) * 60
        seconds = int(decimal_seconds)
        
        return f"{degrees}° {minutes}' {seconds}\" {direction}"
    
    def dms_to_decimal(self, dms_str):
        """Convert DMS string to decimal degrees"""
        try:
            # Remove any spaces around the string and handle empty input
            dms_str = dms_str.strip()
            if not dms_str:
                raise ValueError("Empty input")
            
            # Extract direction (N/S/E/W)
            direction = dms_str[-1].upper()
            if direction not in ['N', 'S', 'E', 'W']:
                raise ValueError("Invalid direction. Must end with N, S, E, or W")
            
            # Remove direction and split into components
            parts = dms_str[:-1].replace('°', ' ').replace("'", ' ').replace('"', ' ').split()
            if len(parts) != 3:
                raise ValueError("Must be in format: DD° MM' SS\" N/S/E/W")
            
            try:
                degrees = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
            except ValueError:
                raise ValueError("Degrees, minutes, and seconds must be numbers")
            
            if not (0 <= minutes < 60 and 0 <= seconds < 60):
                raise ValueError("Minutes and seconds must be between 0 and 59")
            
            decimal = degrees + minutes/60 + seconds/3600
            
            # Apply direction
            if direction in ['S', 'W']:
                decimal = -decimal
                
            return decimal
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError("Invalid DMS format. Use format: DD° MM' SS\" N/S/E/W")
    
    def update_coord_display(self):
        """Update coordinate displays with proper formatting"""
        try:
            lat_text = self.lat_input.text()
            lon_text = self.long_input.text()
            
            # Only convert if the text contains a decimal number
            if '.' in lat_text:
                lat_decimal = float(lat_text)
                self.lat_input.setText(self.decimal_to_dms(lat_decimal, True))
            
            if '.' in lon_text:
                lon_decimal = float(lon_text)
                self.long_input.setText(self.decimal_to_dms(lon_decimal, False))
                
        except ValueError:
            pass

    def validate_dms_input(self, input_field, is_latitude):
        """Validate DMS input and offer conversion if needed"""
        try:
            input_text = input_field.text().strip()
            if not input_text:
                return False

            # Check if it's in DMS format (ends with direction)
            if input_text[-1].upper() in ['N', 'S'] if is_latitude else ['E', 'W']:
                # Try parsing as DMS
                try:
                    parts = input_text[:-1].replace('°', ' ').replace("'", ' ').replace('"', ' ').split()
                    
                    # Handle partial DMS format (without seconds)
                    if len(parts) == 2:  # Only degrees and minutes
                        parts.append('00')  # Add 00 seconds
                        input_text = f"{parts[0]}° {parts[1]}' 00\" {input_text[-1]}"
                        input_field.setText(input_text)
                    elif len(parts) != 3:
                        raise ValueError("Invalid DMS format")
                    
                    degrees = float(parts[0])
                    minutes = float(parts[1])
                    seconds = float(parts[2])
                    
                    # Validate ranges
                    if not (0 <= minutes < 60 and 0 <= seconds < 60):
                        raise ValueError("Minutes and seconds must be between 0 and 59")
                    
                    # Calculate decimal for range validation
                    decimal = degrees + minutes/60 + seconds/3600
                    if input_text[-1] in ['S', 'W']:
                        decimal = -decimal
                        
                    # Validate coordinate ranges
                    if is_latitude and abs(decimal) > 90:
                        raise ValueError("Latitude must be between 90°N and 90°S")
                    elif not is_latitude and abs(decimal) > 180:
                        raise ValueError("Longitude must be between 180°E and 180°W")
                    
                    return True
                    
                except (ValueError, IndexError) as e:
                    QMessageBox.warning(None, "Invalid Input", str(e))
                    return False
            
            # Try decimal format
            try:
                decimal = float(input_text)
                
                # Validate ranges
                if is_latitude and abs(decimal) > 90:
                    raise ValueError("Latitude must be between -90° and 90°")
                elif not is_latitude and abs(decimal) > 180:
                    raise ValueError("Longitude must be between -180° and 180°")
                
                # Ask for conversion to DMS
                coord_type = "latitude" if is_latitude else "longitude"
                dms_format = self.decimal_to_dms(decimal, is_latitude)
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Question)
                msg.setText(f"Would you like to convert this {coord_type} to degrees, minutes, seconds format?")
                msg.setInformativeText(f"Current value: {decimal}\nWill be converted to: {dms_format}")
                msg.setWindowTitle("Convert Coordinate Format")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg.setDefaultButton(QMessageBox.StandardButton.Yes)
                
                if msg.exec() == QMessageBox.StandardButton.Yes:
                    input_field.setText(dms_format)
                return True
                
            except ValueError:
                QMessageBox.warning(None, "Invalid Input", 
                    "Please enter either:\n" +
                    "- DMS format (e.g., 40° 26' N or 40° 26' 46\" N)\n" +
                    "- Decimal format (e.g., 40.446)")
                return False
                
        except Exception as e:
            QMessageBox.warning(None, "Error", str(e))
            return False
    
    def init_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create a widget for input fields
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        input_layout.addLayout(name_layout)
        
        # DateTime input
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Birth Date & Time:"))
        self.date_time = QDateTimeEdit()
        self.date_time.setDateTime(QDateTime.currentDateTime())
        self.date_time.setDisplayFormat("dd/MM/yyyy hh:mm")
        date_layout.addWidget(self.date_time)
        input_layout.addLayout(date_layout)
        
        # City input with search button
        city_layout = QHBoxLayout()
        city_layout.addWidget(QLabel("City:"))
        self.city_input = QLineEdit()
        city_layout.addWidget(self.city_input)
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.fetch_coordinates)
        city_layout.addWidget(search_btn)
        input_layout.addLayout(city_layout)
        
        # Lat/Long inputs with tooltips
        coords_layout = QHBoxLayout()
        coords_layout.addWidget(QLabel("Latitude:"))
        self.lat_input = QLineEdit()
        self.lat_input.setToolTip("Format: DD° MM' N/S or DD° MM' SS\" N/S\nExample: 40° 26' N or 40° 26' 46\" N")
        self.lat_input.setPlaceholderText("e.g., 40° 26' N")
        self.lat_input.editingFinished.connect(lambda: self.validate_dms_input(self.lat_input, True))
        coords_layout.addWidget(self.lat_input)
        
        coords_layout.addWidget(QLabel("Longitude:"))
        self.long_input = QLineEdit()
        self.long_input.setToolTip("Format: DD° MM' E/W or DD° MM' SS\" E/W\nExample: 73° 58' W or 73° 58' 33\" W")
        self.long_input.setPlaceholderText("e.g., 73° 58' W")
        self.long_input.editingFinished.connect(lambda: self.validate_dms_input(self.long_input, False))
        coords_layout.addWidget(self.long_input)
        input_layout.addLayout(coords_layout)
        
        # Add Calculate button
        calc_btn = QPushButton("Calculate Chart")
        calc_btn.clicked.connect(self.calculate_chart)
        input_layout.addWidget(calc_btn)
        
        # Add Settings Section
        settings_group = QGroupBox("Calculation Settings")
        settings_layout = QVBoxLayout()
        
        # Calculation Type (Geocentric vs Topocentric)
        calc_type_layout = QHBoxLayout()
        calc_type_layout.addWidget(QLabel("Calculation Type:"))
        self.calc_type = QComboBox()
        self.calc_type.addItems(["Geocentric", "Topocentric"])
        self.calc_type.setToolTip(
            "Geocentric: Calculated from Earth's center\n"
            "Topocentric: Calculated from the exact birth location"
        )
        calc_type_layout.addWidget(self.calc_type)
        settings_layout.addLayout(calc_type_layout)
        
        # Zodiac System
        zodiac_layout = QHBoxLayout()
        zodiac_layout.addWidget(QLabel("Zodiac System:"))
        self.zodiac_system = QComboBox()
        self.zodiac_system.addItems(["Tropical", "Sidereal"])
        self.zodiac_system.setCurrentText("Sidereal")
        zodiac_layout.addWidget(self.zodiac_system)
        settings_layout.addLayout(zodiac_layout)
        
        # Ayanamsa (enabled for Sidereal)
        ayanamsa_layout = QHBoxLayout()
        ayanamsa_layout.addWidget(QLabel("Ayanamsa:"))
        self.ayanamsa = QComboBox()
        self.ayanamsa.addItems([
            "Lahiri",
            "Raman",
            "Krishnamurti",
            "Fagan/Bradley",
            "True Chitrapaksha"
        ])
        self.ayanamsa.setEnabled(True)
        ayanamsa_layout.addWidget(self.ayanamsa)
        settings_layout.addLayout(ayanamsa_layout)
        
        # Connect zodiac system change to ayanamsa enablement
        self.zodiac_system.currentTextChanged.connect(
            lambda text: self.ayanamsa.setEnabled(text == "Sidereal")
        )
        
        # House System
        house_layout = QHBoxLayout()
        house_layout.addWidget(QLabel("House System:"))
        self.house_system = QComboBox()
        self.house_system.addItems([
            "Placidus",
            "Koch",
            "Equal (Asc)",
            "Equal (MC)",
            "Whole Sign",
            "Campanus",
            "Regiomontanus",
            "Porphyry",
            "Morinus",
            "Meridian",
            "Alcabitius",
            "Azimuthal",
            "Polich/Page (Topocentric)",
            "Vehlow Equal"
        ])
        # Add tooltips for house systems
        self.house_system.setToolTip(
            "Placidus: Traditional western system using time-based division\n"
            "Koch: Similar to Placidus, uses spatial division\n"
            "Equal (Asc): 30° houses starting from Ascendant\n"
            "Equal (MC): 30° houses starting from MC\n"
            "Whole Sign: Each house equals one complete sign\n"
            "Campanus: Uses prime vertical for division\n"
            "Regiomontanus: Uses celestial equator\n"
            "Porphyry: Trisection of quadrants\n"
            "Morinus: Uses equatorial ascensions\n"
            "Meridian: Uses meridian system\n"
            "Alcabitius: Semi-arc system\n"
            "Azimuthal: Uses horizon coordinate system\n"
            "Polich/Page: True local space houses\n"
            "Vehlow Equal: Equal houses with 15° shift"
        )
        house_layout.addWidget(self.house_system)
        settings_layout.addLayout(house_layout)
        
        # Node Type
        node_type_layout = QHBoxLayout()
        node_type_layout.addWidget(QLabel("Node Type:"))
        self.node_type = QComboBox()
        self.node_type.addItems([
            "True Node (Rahu/Ketu)", 
            "Mean Node (Rahu/Ketu)"
        ])
        self.node_type.setToolTip(
            "True Node: Actual position including perturbations\n"
            "Mean Node: Average position without perturbations"
        )
        node_type_layout.addWidget(self.node_type)
        settings_layout.addLayout(node_type_layout)
        
        settings_group.setLayout(settings_layout)
        input_layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.fetch_coords_btn = QPushButton("Fetch Coordinates")
        self.fetch_coords_btn.clicked.connect(self.fetch_coordinates)
        button_layout.addWidget(self.fetch_coords_btn)
        
        self.save_btn = QPushButton("Save Profile")
        self.save_btn.clicked.connect(self.save_profile)
        button_layout.addWidget(self.save_btn)
        
        self.open_btn = QPushButton("Open Profile")
        self.open_btn.clicked.connect(self.open_profile)
        button_layout.addWidget(self.open_btn)
        
        self.dashas_btn = QPushButton("Show Dashas")
        self.dashas_btn.clicked.connect(self.show_dashas)
        button_layout.addWidget(self.dashas_btn)
        
        # Add the new yogeswarananada_12 button
        self.yogeswarananada_btn = QPushButton("yogeswarananada_12")
        self.yogeswarananada_btn.clicked.connect(self.yogeswarananada_handler)
        button_layout.addWidget(self.yogeswarananada_btn)
        
        input_layout.addLayout(button_layout)
        
        input_widget.setLayout(input_layout)
        
        # Create scroll area for results but don't add it to layout yet
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setMinimumHeight(300)
        
        # Create text widget for results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        # Set text widget as scroll area's widget
        self.results_scroll.setWidget(self.results_text)
        self.results_scroll.hide()  # Hide it initially
        
        # Add widgets to main layout
        main_layout.addWidget(input_widget)
        main_layout.addWidget(self.results_scroll)  # Still add it to layout, but it's hidden
        
        # Initialize charts with empty data but don't update until we have real data
        self.northern_chart = NorthernChartWidget()
        
        # Add to layout
        self.chart_stack = QStackedWidget()
        self.chart_stack.addWidget(self.northern_chart)
        self.chart_stack.hide()
        
        main_layout.addWidget(self.chart_stack)
        
        self.setLayout(main_layout)

    def fetch_coordinates(self):
        """Fetch coordinates for the entered city"""
        city = self.city_input.text().strip()
        if not city:
            QMessageBox.warning(self, "Error", "Please enter a city name")
            return
            
        try:
            # Make API request
            geolocator = Nominatim(user_agent="astrology_app")
            location = geolocator.geocode(city)
            if location:
                lat = location.latitude
                lon = location.longitude
                
                # Convert to DMS format
                self.lat_input.setText(self.decimal_to_dms(lat, True))
                self.long_input.setText(self.decimal_to_dms(lon, False))
            else:
                QMessageBox.warning(self, "Error", "City not found")
                
        except GeocoderTimedOut:
            QMessageBox.warning(self, "Error", "Geocoder timed out")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch coordinates: {str(e)}")

    def save_profile(self):
        # Validate inputs
        if not all([self.name_input.text(), self.city_input.text(), 
                    self.lat_input.text(), self.long_input.text()]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
            
        try:
            # Validate coordinates
            lat_str = self.lat_input.text().strip()
            lon_str = self.long_input.text().strip()
            lat_decimal = self.dms_to_decimal(lat_str)
            lon_decimal = self.dms_to_decimal(lon_str)
            
            # Create profile data
            profile_data = {
                "name": self.name_input.text(),
                "datetime": self.date_time.dateTime().toString("dd/MM/yyyy hh:mm"),
                "city": self.city_input.text(),
                "latitude": lat_str,  # Store as DMS string
                "longitude": lon_str,  # Store as DMS string
                "latitude_decimal": lat_decimal,  # Store decimal for calculations
                "longitude_decimal": lon_decimal  # Store decimal for calculations
            }
            
            # Save to file
            with open("profiles.json", "a") as f:
                json.dump(profile_data, f)
                f.write("\n")
            QMessageBox.information(self, "Success", "Profile saved successfully!")
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid coordinates: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save profile: {str(e)}")

    def open_profile(self):
        try:
            # Read all profiles from the file
            profiles = []
            with open("profiles.json", "r") as f:
                for line in f:
                    if line.strip():
                        profiles.append(json.loads(line))
            
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Saved Profiles")
            dialog.setMinimumWidth(600)
            layout = QVBoxLayout()
            
            # Create table
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Name", "Date & Time", "City", "Latitude", "Longitude"])
            table.setRowCount(len(profiles))
            
            # Fill table with data
            for row, profile in enumerate(profiles):
                table.setItem(row, 0, QTableWidgetItem(str(profile.get("name", ""))))
                table.setItem(row, 1, QTableWidgetItem(str(profile.get("datetime", ""))))
                table.setItem(row, 2, QTableWidgetItem(str(profile.get("city", ""))))
                table.setItem(row, 3, QTableWidgetItem(str(profile.get("latitude", ""))))  # Use DMS string
                table.setItem(row, 4, QTableWidgetItem(str(profile.get("longitude", ""))))  # Use DMS string
            
            # Add load button
            def load_selected():
                current_row = table.currentRow()
                if current_row >= 0:
                    profile = profiles[current_row]
                    self.name_input.setText(str(profile.get("name", "")))
                    self.city_input.setText(str(profile.get("city", "")))
                    self.lat_input.setText(str(profile.get("latitude", "")))  # Load DMS string
                    self.long_input.setText(str(profile.get("longitude", "")))  # Load DMS string
                    
                    # Parse and set datetime
                    datetime_str = profile.get("datetime", "")
                    if datetime_str:
                        dt = QDateTime.fromString(datetime_str, "dd/MM/yyyy hh:mm")
                        self.date_time.setDateTime(dt)
                    
                    dialog.accept()
            
            load_btn = QPushButton("Load")
            load_btn.clicked.connect(load_selected)
            
            # Add widgets to layout
            layout.addWidget(table)
            layout.addWidget(load_btn)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except FileNotFoundError:
            QMessageBox.information(self, "Info", "No saved profiles found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load profiles: {str(e)}")

    def get_form_data(self):
        """Get and validate form data."""
        try:
            latitude = float(self.lat_input.text()) if self.lat_input.text().strip() else None
            longitude = float(self.long_input.text()) if self.long_input.text().strip() else None
        except ValueError:
            latitude = None
            longitude = None
        
        return {
            "name": self.name_input.text().strip(),
            "datetime": self.date_time.dateTime(),
            "city": self.city_input.text().strip(),
            "latitude": latitude,
            "longitude": longitude
        }

    def calculate_chart(self):
        """Calculate and display the chart"""
        try:
            # Validate all required fields
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Error", "Please enter a name")
                return
                
            if not self.lat_input.text().strip() or not self.long_input.text().strip():
                QMessageBox.warning(self, "Error", "Please enter both latitude and longitude")
                return
                
            # Get datetime
            birth_time = self.date_time.dateTime()
            if not birth_time.isValid():
                QMessageBox.warning(self, "Error", "Please enter a valid date and time")
                return
                
            # Validate coordinates
            try:
                lat_text = self.lat_input.text().strip()
                lon_text = self.long_input.text().strip()
                
                # Try DMS format first
                try:
                    if lat_text[-1].upper() in ['N', 'S'] and lon_text[-1].upper() in ['E', 'W']:
                        latitude = self.dms_to_decimal(lat_text)
                        longitude = self.dms_to_decimal(lon_text)
                    else:
                        # Try decimal format
                        latitude = float(lat_text)
                        longitude = float(lon_text)
                except (ValueError, IndexError):
                    # Try decimal format as fallback
                    latitude = float(lat_text)
                    longitude = float(lon_text)
                
                # Validate ranges
                if abs(latitude) > 90:
                    raise ValueError("Latitude must be between 90°N and 90°S")
                if abs(longitude) > 180:
                    raise ValueError("Longitude must be between 180°E and 180°W")
                    
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
                return
                
            # Calculate the chart data
            self.chart_data = self.astro_calc.calculate_chart(
                dt=birth_time.toPyDateTime(),
                lat=latitude,
                lon=longitude,
                calc_type=self.calc_type.currentText(),
                zodiac=self.zodiac_system.currentText(),
                ayanamsa=self.ayanamsa.currentText(),
                house_system=self.house_system.currentText(),
                node_type=self.node_type.currentText()
            )
            
            # Enable buttons after successful calculation
            self.yogeswarananada_btn.setEnabled(True)
            self.dashas_btn.setEnabled(True)
            
            # Update the main display
            self.display_results(self.chart_data)
            
            # Find existing chart dialog
            existing_dialog = None
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, ChartDialog):
                    existing_dialog = widget
                    break
            
            if existing_dialog:
                # Update existing chart widget
                existing_dialog.chart_widget.update_data(self.chart_data)
                existing_dialog.chart_widget.update()
            else:
                # Create and show new chart dialog
                chart_widget = NorthernChartWidget(self, input_page=self)
                chart_widget.update_data(self.chart_data)
                dialog = ChartDialog(chart_widget, self)
                dialog.show()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to calculate chart: {str(e)}")
            self.yogeswarananada_btn.setEnabled(False)
            self.dashas_btn.setEnabled(False)

    def display_results(self, chart_data):
        """Display the calculation results."""
        try:
            # Show the results area first
            self.results_scroll.show()
            
            # Add debug logging at the start
            print("Debug - Full chart_data:", json.dumps(chart_data, indent=2))
            
            # Create a formatted text output
            output = f"Calculations for {self.name_input.text()}\n"
            output += f"Date & Time: {chart_data['meta']['datetime']}\n"
            
            # Convert coordinates to DMS format for display
            lat = float(chart_data['meta']['latitude'])
            lon = float(chart_data['meta']['longitude'])
            lat_dms = self.decimal_to_dms(lat, True)
            lon_dms = self.decimal_to_dms(lon, False)
            output += f"Location: {self.city_input.text()} ({lat_dms}, {lon_dms})\n\n"
            
            output += "Planetary Positions:\n"
            output += "-------------------\n"
            
            # Display points in a specific order
            display_order = [
                "Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", 
                "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"
            ]
            
            # Display planetary positions
            for point in display_order:
                if point in chart_data['points']:
                    data = chart_data['points'][point]
                    output += f"{point}:\n"
                    output += f"  Sign: {data['sign']} {self.decimal_to_dms(data['degree'])} (House {data['house']})\n"
                    
                    # Add nakshatra details if available
                    if 'nakshatra' in data:
                        output += f"  Nakshatra: {data['nakshatra']} (Pada {data['pada']})\n"
                        output += f"  Star Lord: {data['star_lord']}\n"
                        output += f"  Sub Lord: {data['sub_lord']}\n"
                    
                    # Add retrograde status if available
                    if 'is_retrograde' in data and data['is_retrograde']:
                        output += "  Status: Retrograde\n"
                    
                    # Add node type if available
                    if 'type' in data:
                        output += f"  Type: {data['type']}\n"
                    
                    output += "\n"
            
            # Add debug logging before house cusps
            print("Debug - Houses data:", json.dumps(chart_data.get('houses', {}), indent=2))
            
            # Add House Cusps section with lords
            output += "\nHouse Cusps:\n"
            output += "------------\n"
            for house in range(1, 13):
                house_key = f"House_{house}"
                if house_key in chart_data.get('houses', {}):
                    house_data = chart_data['houses'][house_key]
                    output += f"House {house}:\n"
                    output += f"  Longitude: {self.decimal_to_dms(house_data['longitude'])}\n"
                    output += f"  Sign: {house_data['sign']} {self.decimal_to_dms(house_data['degree'])}\n"
                    output += f"  Nakshatra: {house_data['nakshatra']} (Pada {house_data['pada']})\n"
                    output += f"  Star Lord: {house_data['star_lord']}\n"
                    output += f"  Sub Lord: {house_data['sub_lord']}\n\n"
            
            # Add calculation settings
            output += "Calculation Settings:\n"
            output += "-------------------\n"
            output += f"Calculation Type: {self.calc_type.currentText()}\n"
            output += f"Zodiac System: {self.zodiac_system.currentText()}\n"
            output += f"Ayanamsa: {self.ayanamsa.currentText()}\n"
            output += f"House System: {self.house_system.currentText()}\n"
            output += f"Node Type: {self.node_type.currentText()}\n"
            
            # Display the results in the QTextEdit widget instead of popup
            self.results_text.setText(output)
            
        except Exception as e:
            print(f"Debug - Error in display_results: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to display results: {str(e)}")

    def show_dashas(self):
        """Display dasha periods in a nested tree format with current period highlighted"""
        if not self.chart_data:
            QMessageBox.warning(self, "Error", "Please calculate the chart first")
            return
            
        try:
            data = self.get_form_data()
            birth_date = data['datetime'].toPyDateTime()
            moon_longitude = self.chart_data["points"]["Moon"]["longitude"]
            
            # Calculate dashas
            dasha_calc = DashaCalculator()
            dashas = dasha_calc.calculate_dashas(birth_date, moon_longitude)
            
            # Create window to display results
            dasha_window = QDialog(self)
            dasha_window.setWindowTitle("Dasha Periods")
            dasha_window.setMinimumWidth(800)
            dasha_window.setMinimumHeight(600)
            layout = QVBoxLayout()
            
            # Create tree widget
            tree = QTreeWidget()
            tree.setHeaderLabels(["Dasha Level", "Period", "Duration"])
            tree.setColumnWidth(0, 300)  # Wider column for nested names
            tree.setColumnWidth(1, 300)  # Wider column for dates
            
            # Get current datetime for comparison
            current_datetime = datetime.now()
            
            def add_dasha_to_tree(dasha, parent=None):
                if parent is None:
                    item = QTreeWidgetItem(tree)
                else:
                    item = QTreeWidgetItem(parent)
                
                # Format the period string
                period = f"{dasha['start_date'].strftime('%Y-%m-%d %H:%M')} to {dasha['end_date'].strftime('%Y-%m-%d %H:%M')}"
                
                item.setText(0, dasha['lord'])
                item.setText(1, period)
                item.setText(2, dasha['duration_str'])
                
                # Check if this period is current
                is_current = (dasha['start_date'] <= current_datetime <= dasha['end_date'])
                
                # Set background color if current
                if is_current:
                    for col in range(3):
                        item.setBackground(col, QtGui.QColor('#FFEB3B'))  # Light yellow highlight
                        item.setForeground(col, QtGui.QColor('#000000'))  # Black text
                
                # Add sub-dashas recursively
                if 'sub_dashas' in dasha:
                    for sub_dasha in dasha['sub_dashas']:
                        add_dasha_to_tree(sub_dasha, item)
                
                # Expand the item if it's current or contains the current period
                if is_current and parent is not None:
                    parent.setExpanded(True)
                
                return item
            
            # Add all dashas to the tree
            for dasha in dashas:
                item = add_dasha_to_tree(dasha)
                # If this main dasha contains current period, expand it
                if current_datetime >= dasha['start_date'] and current_datetime <= dasha['end_date']:
                    item.setExpanded(True)
            
            layout.addWidget(tree)
            dasha_window.setLayout(layout)
            dasha_window.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to calculate dashas: {str(e)}")

    # Add the handler method for the new button
    def yogeswarananada_handler(self):
        try:
            if not self.chart_data:
                QMessageBox.warning(self, "Error", "Please calculate the chart first")
                return
            
            # Create and show the yogeswarananada window
            window = YogeswarananadaWindow(self.chart_data, self)
            window.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def handle_coordinate_change(self):
        try:
            # Validate coordinates
            lat_text = self.lat_input.text().strip()
            lon_text = self.long_input.text().strip()
            
            # Try DMS format first
            try:
                if lat_text[-1].upper() in ['N', 'S'] and lon_text[-1].upper() in ['E', 'W']:
                    latitude = self.dms_to_decimal(lat_text)
                    longitude = self.dms_to_decimal(lon_text)
                else:
                    # Try decimal format
                    latitude = float(lat_text)
                    longitude = float(lon_text)
            except (ValueError, IndexError):
                # Try decimal format as fallback
                latitude = float(lat_text)
                longitude = float(lon_text)
            
            # Validate ranges
            if abs(latitude) > 90:
                raise ValueError("Latitude must be between 90°N and 90°S")
            if abs(longitude) > 180:
                raise ValueError("Longitude must be between 180°E and 180°W")
                
            # Calculate the chart data
            self.chart_data = self.astro_calc.calculate_chart(
                dt=self.date_time.dateTime().toPyDateTime(),
                lat=latitude,
                lon=longitude,
                calc_type=self.calc_type.currentText(),
                zodiac=self.zodiac_system.currentText(),
                ayanamsa=self.ayanamsa.currentText(),
                house_system=self.house_system.currentText(),
                node_type=self.node_type.currentText()
            )
            
            # Enable buttons after successful calculation
            self.yogeswarananada_btn.setEnabled(True)
            self.dashas_btn.setEnabled(True)
            
            # Update the main display
            self.display_results(self.chart_data)
            
            # Find existing chart dialog
            existing_dialog = None
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, ChartDialog):
                    existing_dialog = widget
                    break
            
            if existing_dialog:
                # Update existing chart widget
                existing_dialog.chart_widget.update_data(self.chart_data)
                existing_dialog.chart_widget.update()
            else:
                # Create and show new chart dialog
                chart_widget = NorthernChartWidget(self, input_page=self)
                chart_widget.update_data(self.chart_data)
                dialog = ChartDialog(chart_widget, self)
                dialog.show()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to calculate chart: {str(e)}")
            self.yogeswarananada_btn.setEnabled(False)
            self.dashas_btn.setEnabled(False)
