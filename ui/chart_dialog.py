from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class ChartDialog(QDialog):
    def __init__(self, chart_widget, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Birth Chart")
        self.setMinimumSize(600, 600)
        
        # Store the widget reference
        self.chart_widget = chart_widget
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.chart_widget)
        self.setLayout(layout)
        
        # Make sure the dialog stays on top using the correct flag
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)