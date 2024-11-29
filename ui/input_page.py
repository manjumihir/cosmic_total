import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                           QPushButton, QLabel, QMessageBox, QDialog, 
                           QTableWidget, QTableWidgetItem, QTextEdit, 
                           QGroupBox, QComboBox, QScrollArea, QDateTimeEdit,
                           QTreeWidget, QTreeWidgetItem, QStackedWidget)
from PyQt6.QtCore import QDateTime, Qt
from data.constants import POSITIONSTACK_API_KEY
import requests
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
        
        # City input
        city_layout = QHBoxLayout()
        city_layout.addWidget(QLabel("City:"))
        self.city_input = QLineEdit()
        city_layout.addWidget(self.city_input)
        input_layout.addLayout(city_layout)
        
        # Lat/Long inputs
        coords_layout = QHBoxLayout()
        coords_layout.addWidget(QLabel("Latitude:"))
        self.lat_input = QLineEdit()
        coords_layout.addWidget(self.lat_input)
        coords_layout.addWidget(QLabel("Longitude:"))
        self.long_input = QLineEdit()
        coords_layout.addWidget(self.long_input)
        input_layout.addLayout(coords_layout)
        
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
        
        self.calc_btn = QPushButton("Calculate")
        self.calc_btn.clicked.connect(self.calculate_chart)
        button_layout.addWidget(self.calc_btn)
        
        # Add the new yogeswarananada_12 button
        self.yogeswarananada_btn = QPushButton("yogeswarananada_12")
        self.yogeswarananada_btn.clicked.connect(self.yogeswarananada_handler)
        button_layout.addWidget(self.yogeswarananada_btn)
        
        self.dashas_btn = QPushButton("Show Dashas")
        self.dashas_btn.clicked.connect(self.show_dashas)
        button_layout.addWidget(self.dashas_btn)
        
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
        city = self.city_input.text().strip()
        if not city:
            QMessageBox.warning(self, "Error", "Please enter a city name")
            return
            
        try:
            url = f"http://api.positionstack.com/v1/forward?access_key={POSITIONSTACK_API_KEY}&query={city}"
            response = requests.get(url)
            data = response.json()
            
            if data.get('data'):
                location = data['data'][0]
                self.lat_input.setText(str(location['latitude']))
                self.long_input.setText(str(location['longitude']))
            else:
                QMessageBox.warning(self, "Error", "City not found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch coordinates: {str(e)}")

    def save_profile(self):
        # Validate inputs
        if not all([self.name_input.text(), self.city_input.text(), 
                    self.lat_input.text(), self.long_input.text()]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
            
        # Create profile data
        profile_data = {
            "name": self.name_input.text(),
            "datetime": self.date_time.dateTime().toString("dd/MM/yyyy hh:mm"),
            "city": self.city_input.text(),
            "latitude": float(self.lat_input.text()),
            "longitude": float(self.long_input.text())
        }
        
        # Save to file (you might want to use a database instead)
        try:
            with open("profiles.json", "a") as f:
                json.dump(profile_data, f)
                f.write("\n")
            QMessageBox.information(self, "Success", "Profile saved successfully!")
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
                table.setItem(row, 3, QTableWidgetItem(str(profile.get("latitude", ""))))
                table.setItem(row, 4, QTableWidgetItem(str(profile.get("longitude", ""))))
            
            # Add load button
            def load_selected():
                current_row = table.currentRow()
                if current_row >= 0:
                    profile = profiles[current_row]
                    self.name_input.setText(str(profile.get("name", "")))
                    self.city_input.setText(str(profile.get("city", "")))
                    self.lat_input.setText(str(profile.get("latitude", "")))
                    self.long_input.setText(str(profile.get("longitude", "")))
                    
                    # Parse and set datetime
                    datetime_str = profile.get("datetime", "")
                    if datetime_str:
                        dt = QDateTime.fromString(datetime_str, "dd/MM/yyyy hh:mm")
                        self.date_time.setDateTime(dt)
                    
                    # Load calculation settings
                    if "zodiac_system" in profile:
                        self.zodiac_system.setCurrentText(profile["zodiac_system"])
                        # Make sure to enable/disable ayanamsa based on zodiac system
                        self.ayanamsa.setEnabled(profile["zodiac_system"] == "Sidereal")
                    if "ayanamsa" in profile:
                        self.ayanamsa.setCurrentText(profile["ayanamsa"])
                    
                    dialog.accept()
            
            load_btn = QPushButton("Load Selected")
            load_btn.clicked.connect(load_selected)
            
            layout.addWidget(table)
            layout.addWidget(load_btn)
            dialog.setLayout(layout)
            
            # Show dialog
            dialog.exec()
            
        except FileNotFoundError:
            QMessageBox.information(self, "Info", "No saved profiles found.")
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
            # Basic validation first
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Error", "Please enter a name")
                return
                
            # Validate coordinates
            try:
                latitude = float(self.lat_input.text())
                longitude = float(self.long_input.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "Please enter valid latitude and longitude values")
                return
                
            # Get datetime
            birth_time = self.date_time.dateTime()
            if not birth_time.isValid():
                QMessageBox.warning(self, "Error", "Please enter a valid date and time")
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
            
            # Create and show the chart dialog
            chart_widget = NorthernChartWidget(self, input_page=self)
            chart_widget.update_data(self.chart_data)
            
            dialog = ChartDialog(chart_widget, self)
            dialog.show()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to calculate chart: {str(e)}")
            self.yogeswarananada_btn.setEnabled(False)
            self.dashas_btn.setEnabled(False)

    def decimal_to_dms(self, decimal_degrees):
        """Convert decimal degrees to degrees, minutes, and seconds"""
        degrees = int(decimal_degrees)
        decimal_minutes = (decimal_degrees - degrees) * 60
        minutes = int(decimal_minutes)
        decimal_seconds = (decimal_minutes - minutes) * 60
        seconds = int(decimal_seconds)
        return f"{degrees}°{minutes:02d}'{seconds:02d}\""

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
            output += f"Location: {self.city_input.text()} ({chart_data['meta']['latitude']}, {chart_data['meta']['longitude']})\n\n"
            
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
