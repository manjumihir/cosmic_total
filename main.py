import sys
import os
print("Current Python version:", sys.version)
print("Current working directory:", os.getcwd())

print("Python interpreter path:", sys.executable)
print("Python path:", sys.path)

import site
print("Site packages:", site.getsitepackages())

try:
    import kerykeion
    print("Kerykeion found at:", kerykeion.__file__)
except ImportError as e:
    print("Failed to import kerykeion:", e)
    import traceback
    traceback.print_exc()

import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
import logging
import swisseph as swe
from data.constants import EPHEMERIS_PATH
import json

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def setup_ephemeris():
    """Set up Swiss Ephemeris"""
    swe.set_ephe_path(EPHEMERIS_PATH)

def main():
    # Initialize logging
    setup_logging()
    
    # Initialize Swiss Ephemeris
    setup_ephemeris()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
