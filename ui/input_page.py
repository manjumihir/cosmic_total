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
from .yogeswarananda_window import YogeswarananadaWindow
from .chart_widgets import NorthernChartWidget
from .chart_dialog import ChartDialog
from .results_window import ResultsWindow

class InputPage(QWidget):
    def __init__(self):
        super().__init__()
        self.astro_calc = AstroCalc()
        self.chart_data = None
        self.results_window = None
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
        # Create main layout with proper margins
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create scroll area for all content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Main container widget
        container = QWidget()
        container.setMinimumWidth(800)  # Set minimum width for container
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        
        # Personal Information Group
        personal_group = QGroupBox("Personal Information")
        personal_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        personal_layout = QVBoxLayout()
        personal_layout.setSpacing(10)
        
        # Name input with proper spacing
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setMinimumWidth(100)
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        personal_layout.addLayout(name_layout)
        
        # DateTime input
        date_layout = QHBoxLayout()
        date_label = QLabel("Birth Date & Time:")
        date_label.setMinimumWidth(100)
        self.date_time = QDateTimeEdit()
        self.date_time.setDateTime(QDateTime.currentDateTime())
        self.date_time.setDisplayFormat("dd/MM/yyyy hh:mm")
        self.date_time.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_time)
        personal_layout.addLayout(date_layout)
        
        personal_group.setLayout(personal_layout)
        container_layout.addWidget(personal_group)
        
        # Location Group
        location_group = QGroupBox("Location Information")
        location_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        location_layout = QVBoxLayout()
        location_layout.setSpacing(10)
        
        # City input with search
        city_layout = QHBoxLayout()
        city_label = QLabel("City:")
        city_label.setMinimumWidth(100)
        self.city_input = QLineEdit()
        search_btn = QPushButton("Search")
        search_btn.setMaximumWidth(100)
        search_btn.clicked.connect(self.fetch_coordinates)
        city_layout.addWidget(city_label)
        city_layout.addWidget(self.city_input)
        city_layout.addWidget(search_btn)
        location_layout.addLayout(city_layout)
        
        # Coordinates
        coords_layout = QHBoxLayout()
        # Latitude
        lat_layout = QHBoxLayout()
        lat_label = QLabel("Latitude:")
        lat_label.setMinimumWidth(100)
        self.lat_input = QLineEdit()
        self.lat_input.setMinimumWidth(200)  # Set minimum width for input
        self.lat_input.setToolTip("Format: DD° MM' N/S or DD° MM' SS\" N/S\nExample: 40° 26' N")
        self.lat_input.setPlaceholderText("e.g., 40° 26' N")
        self.lat_input.editingFinished.connect(lambda: self.validate_dms_input(self.lat_input, True))
        lat_layout.addWidget(lat_label)
        lat_layout.addWidget(self.lat_input)
        
        # Longitude
        lon_layout = QHBoxLayout()
        lon_label = QLabel("Longitude:")
        lon_label.setMinimumWidth(100)
        self.long_input = QLineEdit()
        self.long_input.setMinimumWidth(200)  # Set minimum width for input
        self.long_input.setToolTip("Format: DD° MM' E/W or DD° MM' SS\" E/W\nExample: 73° 58' W")
        self.long_input.setPlaceholderText("e.g., 73° 58' W")
        self.long_input.editingFinished.connect(lambda: self.validate_dms_input(self.long_input, False))
        lon_layout.addWidget(lon_label)
        lon_layout.addWidget(self.long_input)
        
        coords_layout.addLayout(lat_layout)
        coords_layout.addLayout(lon_layout)
        location_layout.addLayout(coords_layout)
        
        location_group.setLayout(location_layout)
        container_layout.addWidget(location_group)
        
        # Calculation Settings Group
        settings_group = QGroupBox("Calculation Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(10)
        
        # Create two columns for settings
        settings_columns = QHBoxLayout()
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()
        
        # Left Column Settings
        # Calculation Type
        calc_type_layout = QHBoxLayout()
        calc_type_label = QLabel("Calculation Type:")
        calc_type_label.setMinimumWidth(120)
        self.calc_type = QComboBox()
        self.calc_type.addItems(["Geocentric", "Topocentric"])
        self.calc_type.setToolTip("Geocentric: Earth's center\nTopocentric: Birth location")
        self.calc_type.setMinimumWidth(200)  # Set minimum width for combo box
        calc_type_layout.addWidget(calc_type_label)
        calc_type_layout.addWidget(self.calc_type)
        left_column.addLayout(calc_type_layout)
        
        # Zodiac System
        zodiac_layout = QHBoxLayout()
        zodiac_label = QLabel("Zodiac System:")
        zodiac_label.setMinimumWidth(120)
        self.zodiac_system = QComboBox()
        self.zodiac_system.addItems(["Tropical", "Sidereal"])
        self.zodiac_system.setCurrentText("Sidereal")
        self.zodiac_system.setMinimumWidth(200)  # Set minimum width for combo box
        zodiac_layout.addWidget(zodiac_label)
        zodiac_layout.addWidget(self.zodiac_system)
        left_column.addLayout(zodiac_layout)
        
        # Ayanamsa
        ayanamsa_layout = QHBoxLayout()
        ayanamsa_label = QLabel("Ayanamsa:")
        ayanamsa_label.setMinimumWidth(120)
        self.ayanamsa = QComboBox()
        self.ayanamsa.addItems(["Lahiri", "Raman", "Krishnamurti", "Fagan/Bradley", "True Chitrapaksha"])
        self.ayanamsa.setMinimumWidth(200)  # Set minimum width for combo box
        ayanamsa_layout.addWidget(ayanamsa_label)
        ayanamsa_layout.addWidget(self.ayanamsa)
        left_column.addLayout(ayanamsa_layout)
        
        # Right Column Settings
        # House System
        house_layout = QHBoxLayout()
        house_label = QLabel("House System:")
        house_label.setMinimumWidth(120)
        self.house_system = QComboBox()
        self.house_system.addItems([
            "Placidus", "Koch", "Equal (Asc)", "Equal (MC)", "Whole Sign",
            "Campanus", "Regiomontanus", "Porphyry", "Morinus", "Meridian",
            "Alcabitius", "Azimuthal", "Polich/Page (Topocentric)", "Vehlow Equal"
        ])
        self.house_system.setMinimumWidth(200)  # Set minimum width for combo box
        house_layout.addWidget(house_label)
        house_layout.addWidget(self.house_system)
        right_column.addLayout(house_layout)
        
        # Node Type
        node_layout = QHBoxLayout()
        node_label = QLabel("Node Type:")
        node_label.setMinimumWidth(120)
        self.node_type = QComboBox()
        self.node_type.addItems(["True Node (Rahu/Ketu)", "Mean Node (Rahu/Ketu)"])
        self.node_type.setMinimumWidth(200)  # Set minimum width for combo box
        node_layout.addWidget(node_label)
        node_layout.addWidget(self.node_type)
        right_column.addLayout(node_layout)
        
        # Add columns to settings layout
        settings_columns.addLayout(left_column)
        settings_columns.addLayout(right_column)
        settings_layout.addLayout(settings_columns)
        
        settings_group.setLayout(settings_layout)
        container_layout.addWidget(settings_group)
        
        # Actions Group
        actions_group = QGroupBox("Actions")
        actions_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        actions_layout = QVBoxLayout()
        
        # Primary actions
        primary_actions = QHBoxLayout()
        
        # Calculate button with prominence
        calc_btn = QPushButton("Calculate Chart")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B4EAE;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #563D8C;
            }
        """)
        calc_btn.clicked.connect(self.calculate_chart)
        primary_actions.addWidget(calc_btn)
        
        # Secondary actions
        secondary_actions = QHBoxLayout()
        secondary_actions.setSpacing(10)
        
        # Profile management buttons
        self.save_btn = QPushButton("Save Profile")
        self.open_btn = QPushButton("Open Profile")
        self.dashas_btn = QPushButton("Show Dashas")
        self.yogeswarananada_btn = QPushButton("Yogeswarananada")
        
        for btn in [self.save_btn, self.open_btn, self.dashas_btn, self.yogeswarananada_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    border: 1px solid #6B4EAE;
                    border-radius: 4px;
                    color: #6B4EAE;
                }
                QPushButton:hover {
                    background-color: #F0E6FF;
                }
            """)
            secondary_actions.addWidget(btn)
        
        self.save_btn.clicked.connect(self.save_profile)
        self.open_btn.clicked.connect(self.open_profile)
        self.dashas_btn.clicked.connect(self.show_dashas)
        self.yogeswarananada_btn.clicked.connect(self.yogeswarananada_handler)
        
        actions_layout.addLayout(primary_actions)
        actions_layout.addLayout(secondary_actions)
        actions_group.setLayout(actions_layout)
        container_layout.addWidget(actions_group)
        
        # Set up the container
        container.setLayout(container_layout)
        scroll.setWidget(container)
        
        # Add everything to main layout
        main_layout.addWidget(scroll)
        
        # Connect zodiac system change to ayanamsa enablement
        self.zodiac_system.currentTextChanged.connect(
            lambda text: self.ayanamsa.setEnabled(text == "Sidereal")
        )
        
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
            
            # Create or show results window
            if not self.results_window:
                self.results_window = ResultsWindow(self)
            
            # Generate and display results
            html_content = self.generate_html_results(self.chart_data)
            self.results_window.set_html_content(html_content)
            self.results_window.show()
            self.results_window.raise_()  # Bring window to front
            
            # Find existing chart dialog
            existing_dialog = None
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, ChartDialog) and not widget.isHidden():
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

    def generate_html_results(self, chart_data):
        """Generate HTML formatted results."""
        try:
            # Create HTML template with CSS styling
            html_output = """
            <html>
            <head>
                <style>
                    body {
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: #FFFFFF;
                        padding: 20px;
                        background-color: #000000;
                    }
                    .header {
                        background: #1A1A1A;
                        color: white;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 20px;
                        border: 1px solid #333333;
                    }
                    .section {
                        background: #1A1A1A;
                        border: 1px solid #333333;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 20px;
                    }
                    .section-title {
                        color: #FFFFFF;
                        border-bottom: 2px solid #333333;
                        padding-bottom: 5px;
                        margin-bottom: 15px;
                        font-weight: bold;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 15px;
                    }
                    th, td {
                        padding: 8px;
                        text-align: left;
                        border: 1px solid #333333;
                    }
                    th {
                        background: #262626;
                        color: #FFFFFF;
                        font-weight: bold;
                    }
                    tr:nth-child(even) {
                        background: #1F1F1F;
                    }
                    tr:nth-child(odd) {
                        background: #262626;
                    }
                    .planet-card, .house-card {
                        background: #1F1F1F;
                        border: 1px solid #333333;
                        border-radius: 6px;
                        padding: 10px;
                        margin-bottom: 10px;
                    }
                    .settings-item {
                        display: inline-block;
                        background: #262626;
                        border-radius: 4px;
                        padding: 5px 10px;
                        margin: 5px;
                        border: 1px solid #333333;
                    }
                    .retrograde {
                        color: #FF6B6B;
                        font-weight: bold;
                    }
                    .coordinates {
                        color: #66B2FF;
                        font-weight: 500;
                    }
                </style>
            </head>
            <body>
            """
            
            # Header Section
            html_output += f"""
            <div class="header">
                <h2>Astrological Chart for {self.name_input.text()}</h2>
                <p>Date & Time: {chart_data['meta']['datetime']}</p>
                <p>Location: {self.city_input.text()} 
                   <span class="coordinates">({self.decimal_to_dms(float(chart_data['meta']['latitude']), True)}, 
                   {self.decimal_to_dms(float(chart_data['meta']['longitude']), False)})</span>
                </p>
            </div>
            """
            
            # Planetary Positions Section
            html_output += '<div class="section"><h3 class="section-title">Planetary Positions</h3>'
            html_output += '<table>'
            html_output += '<tr><th>Planet</th><th>Sign & Position</th><th>House</th><th>Nakshatra</th><th>Star Lord</th><th>Sub Lord</th><th>Status</th></tr>'
            
            display_order = [
                "Ascendant", "Sun", "Moon", "Mars", "Mercury", "Jupiter", 
                "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"
            ]
            
            for point in display_order:
                if point in chart_data['points']:
                    data = chart_data['points'][point]
                    html_output += '<tr>'
                    html_output += f'<td>{point}</td>'
                    html_output += f'<td>{data["sign"]} {self.decimal_to_dms(data["degree"])}</td>'
                    html_output += f'<td>{data["house"]}</td>'
                    
                    if 'nakshatra' in data:
                        html_output += f'<td>{data["nakshatra"]} (Pada {data["pada"]})</td>'
                        html_output += f'<td>{data["star_lord"]}</td>'
                        html_output += f'<td>{data["sub_lord"]}</td>'
                    else:
                        html_output += '<td>-</td><td>-</td><td>-</td>'
                    
                    status = []
                    if 'is_retrograde' in data and data['is_retrograde']:
                        status.append('<span class="retrograde">Retrograde</span>')
                    if 'type' in data:
                        status.append(data["type"])
                    html_output += f'<td>{" ".join(status) if status else "-"}</td>'
                    
                    html_output += '</tr>'
            
            html_output += '</table></div>'
            
            # House Cusps Section
            html_output += '<div class="section"><h3 class="section-title">House Cusps</h3>'
            html_output += '<table>'
            html_output += '<tr><th>House</th><th>Sign & Position</th><th>Nakshatra</th><th>Star Lord</th><th>Sub Lord</th></tr>'
            
            for house in range(1, 13):
                house_key = f"House_{house}"
                if house_key in chart_data.get('houses', {}):
                    house_data = chart_data['houses'][house_key]
                    html_output += '<tr>'
                    html_output += f'<td>{house}</td>'
                    html_output += f'<td>{house_data["sign"]} {self.decimal_to_dms(house_data["degree"])}</td>'
                    html_output += f'<td>{house_data["nakshatra"]} (Pada {house_data["pada"]})</td>'
                    html_output += f'<td>{house_data["star_lord"]}</td>'
                    html_output += f'<td>{house_data["sub_lord"]}</td>'
                    html_output += '</tr>'
            
            html_output += '</table></div>'
            
            # Settings Section
            html_output += '<div class="section"><h3 class="section-title">Calculation Settings</h3>'
            html_output += '<div class="settings-container">'
            html_output += f'<span class="settings-item">Calculation Type: {self.calc_type.currentText()}</span>'
            html_output += f'<span class="settings-item">Zodiac System: {self.zodiac_system.currentText()}</span>'
            html_output += f'<span class="settings-item">Ayanamsa: {self.ayanamsa.currentText()}</span>'
            html_output += f'<span class="settings-item">House System: {self.house_system.currentText()}</span>'
            html_output += f'<span class="settings-item">Node Type: {self.node_type.currentText()}</span>'
            html_output += '</div></div>'
            
            html_output += '</body></html>'
            
            return html_output
            
        except Exception as e:
            print(f"Debug - Error generating HTML results: {str(e)}")
            raise

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
