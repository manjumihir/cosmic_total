from PyQt6.QtWidgets import QMainWindow, QTextEdit, QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ResultsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chart Results")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #000000; }")
        
        # Create text widget
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        # Set font
        font = QFont("Segoe UI", 10)
        self.results_text.setFont(font)
        
        # Style the text widget
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: none;
                selection-background-color: #404040;
                selection-color: #FFFFFF;
            }
        """)
        
        # Add text widget to scroll area
        scroll.setWidget(self.results_text)
        
        # Add scroll area to layout
        layout.addWidget(scroll)
        
        # Set window flags for a detached window
        self.setWindowFlags(Qt.WindowType.Window)
    
    def set_html_content(self, html_content):
        """Set the HTML content of the results window"""
        self.results_text.setHtml(html_content)
        
    def closeEvent(self, event):
        """Handle window close event"""
        self.hide()  # Hide instead of close to preserve the window
        event.ignore()
