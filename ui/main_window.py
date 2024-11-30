from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from ui.input_page import InputPage
from .results_page import ResultsPage
from ui.chart_widgets import NorthernChartWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Birth Data Input")
        self.setMinimumWidth(900)  # Set minimum width for the window
        
        # Create stacked widget to manage multiple pages
        self.stacked_widget = QStackedWidget()
        self.input_page = InputPage()
        self.results_page = ResultsPage()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.input_page)
        self.stacked_widget.addWidget(self.results_page)
        
        self.setCentralWidget(self.stacked_widget)
        
        # Create chart widget and add it to results page
        self.chart_widget = NorthernChartWidget(None)
        self.results_page.layout.addWidget(self.chart_widget)
        
    def set_data(self, data):
        """Handle the data after calculation"""
        self.data = data
        print(f"Received data: {self.data}")  # Debug
        
        # Update chart widget with the new data
        chart_data = {
            'points': self.data.get('points', {}),
            'houses': self.data.get('houses', {})
        }
        print(f"Updated points: {len(chart_data['points'])}, houses: {len(chart_data['houses'])}")  # Debug
        self.chart_widget.update_data(chart_data)
        
        # Update results page and switch to it
        self.results_page.update_data(self.data)
        self.stacked_widget.setCurrentWidget(self.results_page)

    def update_chart(self, natal_data, transit_data=None):
        """Update chart with both natal and transit data"""
        self.chart_widget.update_data(natal_data)
        if transit_data:
            self.chart_widget.update_transit_data(transit_data)