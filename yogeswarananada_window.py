from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QMessageBox, QTabWidget, QWidget)
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class YogeswarananadaWindow(QDialog):
    def __init__(self, chart_data, parent=None):
        super().__init__(parent)
        self.chart_data = chart_data
        self.house_points = {i: 0 for i in range(1, 13)}
        self.calculation_results = []  # Store results for plotting
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Yogeswarananada Calculations")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(800)
        
        # Create main layout
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Text output tab
        text_tab = QWidget()
        text_layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        text_layout.addWidget(self.results_text)
        text_tab.setLayout(text_layout)
        
        # Chart tab
        chart_tab = QWidget()
        chart_layout = QVBoxLayout()
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        chart_tab.setLayout(chart_layout)
        
        # Add tabs
        self.tabs.addTab(text_tab, "Detailed Calculations")
        self.tabs.addTab(chart_tab, "House Strength Charts")
        
        # Add tabs to main layout
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        # Calculate and display results
        self.calculate_results()  # Changed from calculate_yogeswarananada()
        self.update_charts()

    def calculate_results(self):
        """Calculate results for all planets in the chart"""
        output = ""
        self.calculation_results = []  # Reset results
        
        for planet, data in self.chart_data['points'].items():
            output += f"\n=== Calculation for {planet} ===\n"
            output += self.calculate_single_planet(planet, "Planet")
            output += "\n" + "="*40 + "\n"
        
        self.results_text.setText(output)

    def update_charts(self):
        """Create visualizations for the calculations"""
        self.figure.clear()
        
        # Create subplots based on number of calculations
        num_calcs = len(self.calculation_results)
        rows = (num_calcs + 1) // 2  # Two charts per row
        cols = min(2, num_calcs)
        
        for idx, calc in enumerate(self.calculation_results):
            ax = self.figure.add_subplot(rows, cols, idx + 1)
            
            # Extract data
            houses = list(range(1, 13))
            points = [calc['points'][h] for h in houses]
            
            # Create bars
            bars = ax.bar(houses, points)
            
            # Color bars based on point values
            for bar, point in zip(bars, points):
                if point > 15:
                    bar.set_color('red')
                elif point > 10:
                    bar.set_color('orange')
                else:
                    bar.set_color('blue')
            
            # Customize chart
            ax.set_title(calc['name'])
            ax.set_xlabel('Houses')
            ax.set_ylabel('Points')
            ax.set_xticks(houses)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom')
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def calculate_house_strengths(self, planet, star_lord, sub_lord):
        """Calculate house strengths based on planet, star lord, and sub lord"""
        # Reset house points for new calculation
        self.house_points = {i: 0 for i in range(1, 13)}
        
        # Example implementation - you'll need to replace this with your actual calculation logic
        for house in range(1, 13):
            # Placeholder calculation - replace with actual logic
            self.house_points[house] = house  # Simple placeholder that assigns points equal to house number
        
        return f"House strength calculations completed for {planet} with {star_lord} and {sub_lord}\n"

    def calculate_single_planet(self, planet, role):
        """Modified to store results for plotting"""
        x_data = self.chart_data['points'][planet]
        y = x_data['star_lord']
        z = x_data['sub_lord']
        
        details = f"Planets Involved:\n"
        details += f"{role} (X): {planet}\n"
        details += f"Star Lord (Y): {y}\n"
        details += f"Sub Lord (Z): {z}\n\n"
        
        details += self.calculate_house_strengths(planet, y, z)
        details += "\nResults:\n"
        
        # Store results for plotting
        self.calculation_results.append({
            'name': f"{role} ({planet})",
            'points': self.house_points.copy()
        })
        
        for house, points in self.house_points.items():
            details += f"House {house}: {points} points\n"
        
        return details

    # [Keep all other methods unchanged] 

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    # Sample chart data for testing
    test_chart_data = {
        'points': {
            'Sun': {'star_lord': 'Moon', 'sub_lord': 'Mars'},
            # Add more test data as needed
        }
    }
    
    app = QApplication(sys.argv)
    window = YogeswarananadaWindow(test_chart_data)
    window.show()
    sys.exit(app.exec())