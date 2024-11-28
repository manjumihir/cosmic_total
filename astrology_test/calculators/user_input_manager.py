import os
import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
    QMessageBox, QFileDialog
)
import requests

class UserInputManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.fields = {}
        self.profiles = {}
        self.PROFILE_PATH = "profiles.json"
        self.POSITIONSTACK_API_KEY = 'df58d69f3a320dd1da9f2e805bacf8c9'

    def create_input_tab(self):
        """Create and return the chart input tab"""
        chart_input_tab = QWidget()
        layout = QGridLayout(chart_input_tab)
        
        # Create input fields
        labels = ["Name", "City", "Latitude", "Longitude", "Year",
                 "Month", "Day", "Hour", "Minute", "Second"]
        row = 0
        for label_text in labels:
            label = QLabel(label_text)
            entry = QLineEdit()
            self.fields[label_text.lower()] = entry
            layout.addWidget(label, row, 0)
            layout.addWidget(entry, row, 1)
            row += 1

        # Add buttons
        fetch_coordinates_btn = QPushButton("Fetch Coordinates")
        fetch_coordinates_btn.clicked.connect(self.fetch_coordinates)
        layout.addWidget(fetch_coordinates_btn, row, 0)
        row += 1

        calculate_btn = QPushButton("Calculate")
        calculate_btn.clicked.connect(self.parent.calculate if self.parent else None)
        layout.addWidget(calculate_btn, row, 0)

        return chart_input_tab

    def load_profiles(self):
        """Load saved profiles from file"""
        if os.path.exists(self.PROFILE_PATH):
            with open(self.PROFILE_PATH, "r") as file:
                self.profiles = json.load(file)
        else:
            self.profiles = {}

    def save_profiles(self):
        """Save profiles to file"""
        with open(self.PROFILE_PATH, "w") as file:
            json.dump(self.profiles, file)

    def fetch_coordinates(self):
        """Fetch coordinates for given city using PositionStack API"""
        city_name = self.fields["city"].text()
        if not city_name:
            QMessageBox.critical(self.parent, "Error", "Please enter the city name.")
            return

        try:
            response = requests.get(
                "http://api.positionstack.com/v1/forward",
                params={"access_key": self.df58d69f3a320dd1da9f2e805bacf8c9, "query": city_name}
            )
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                latitude = data["data"][0]["latitude"]
                longitude = data["data"][0]["longitude"]
                self.fields["latitude"].setText(str(latitude))
                self.fields["longitude"].setText(str(longitude))
            else:
                raise ValueError("No data found for the city.")
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Unable to fetch coordinates: {str(e)}")

    def get_input_values(self):
        """Get all input field values"""
        return {key: entry.text() for key, entry in self.fields.items()}

    def set_input_values(self, values):
        """Set input field values"""
        for key, value in values.items():
            if key in self.fields:
                self.fields[key].setText(str(value))

    def clear_inputs(self):
        """Clear all input fields"""
        for entry in self.fields.values():
            entry.clear()

    def save_chart(self):
        """Save current chart data to file"""
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent, 
            "Save Chart", 
            "", 
            "Chart Files (*.chart);;All Files (*)"
        )
        if file_name:
            chart_data = {
                "fields": self.get_input_values(),
                "settings": {
                    "Zodiac System": "Sidereal" if self.parent.sidereal_radio.isChecked() else "Tropical",
                    "Calculation Mode": "Geocentric" if self.parent.geocentric_radio.isChecked() else "Topocentric",
                    "House System": self.parent.house_system_combo.currentText(),
                    "Ayanamsa": self.parent.ayanamsa_combo.currentText(),
                    "Sunrise Calculation": self.parent.sunrise_combo.currentText(),
                    "Data Source": self.parent.data_source_combo.currentText()
                }
            }
            try:
                with open(file_name, 'w') as file:
                    json.dump(chart_data, file)
                QMessageBox.information(self.parent, "Chart Saved", f"Chart saved to {file_name}.")
            except Exception as e:
                QMessageBox.critical(self.parent, "Error", f"Failed to save chart: {str(e)}")

    def open_chart(self):
        """Open and load saved chart data"""
        file_name, _ = QFileDialog.getOpenFileName(
            self.parent, 
            "Open Chart", 
            "", 
            "Chart Files (*.chart);;All Files (*)"
        )
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    chart_data = json.load(file)
                self.set_input_values(chart_data["fields"])
                
                # Update settings
                settings = chart_data.get("settings", {})
                self.parent.sidereal_radio.setChecked(settings.get("Zodiac System", "Tropical") == "Sidereal")
                self.parent.tropical_radio.setChecked(settings.get("Zodiac System", "Tropical") == "Tropical")
                self.parent.geocentric_radio.setChecked(settings.get("Calculation Mode", "Geocentric") == "Geocentric")
                self.parent.topocentric_radio.setChecked(settings.get("Calculation Mode", "Geocentric") == "Topocentric")
                self.parent.house_system_combo.setCurrentText(settings.get("House System", "Placidus"))
                self.parent.ayanamsa_combo.setCurrentText(settings.get("Ayanamsa", "Lahiri"))
                self.parent.sunrise_combo.setCurrentText(settings.get("Sunrise Calculation", "Center of Sun"))
                self.parent.data_source_combo.setCurrentText(settings.get("Data Source", "Swiss Ephemeris"))
                
                QMessageBox.information(self.parent, "Chart Loaded", f"Chart loaded from {file_name}.")
            except Exception as e:
                QMessageBox.critical(self.parent, "Error", f"Failed to open chart: {str(e)}") 