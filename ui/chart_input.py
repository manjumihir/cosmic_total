from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QGridLayout, 
    QPushButton, QMessageBox
)
import requests
from data.constants import POSITIONSTACK_API_KEY

class ChartInputTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.fields = {}
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)
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

        fetch_coordinates_btn = QPushButton("Fetch Coordinates")
        fetch_coordinates_btn.clicked.connect(self.fetch_coordinates)
        layout.addWidget(fetch_coordinates_btn, row, 0)
        row += 1

        calculate_btn = QPushButton("Calculate")
        calculate_btn.clicked.connect(self.parent.calculate if self.parent else None)
        layout.addWidget(calculate_btn, row, 0)

    def fetch_coordinates(self):
        city_name = self.fields["city"].text()
        if not city_name:
            QMessageBox.critical(self, "Error", "Please enter the city name.")
            return

        try:
            response = requests.get(
                "http://api.positionstack.com/v1/forward",
                params={"access_key": POSITIONSTACK_API_KEY, "query": city_name}
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
            QMessageBox.critical(self, "Error", f"Unable to fetch coordinates: {str(e)}")

    def get_values(self):
        """Get all input field values"""
        return {key: entry.text() for key, entry in self.fields.items()}

    def set_values(self, values):
        """Set input field values"""
        for key, value in values.items():
            if key in self.fields:
                self.fields[key].setText(str(value))

    def clear(self):
        """Clear all input fields"""
        for entry in self.fields.values():
            entry.clear() 