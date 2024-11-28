from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ResultsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Initialize your UI elements
        self.name_label = QLabel()
        self.datetime_label = QLabel()
        self.location_label = QLabel()
        
        # Add widgets to layout
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.datetime_label)
        self.layout.addWidget(self.location_label)
        
    def update_data(self, data):
        # Update the UI with the received data
        self.name_label.setText(f"Name: {data['name']}")
        self.datetime_label.setText(f"Date/Time: {data['datetime'].toString()}")
        self.location_label.setText(f"Location: {data['city']} ({data['latitude']}, {data['longitude']})")

    def set_data(self, data):
        """Method to receive and process data from input page"""
        self.update_data(data)