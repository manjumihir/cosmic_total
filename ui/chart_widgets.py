import traceback
from PyQt6 import QtWidgets, QtGui, QtSvg, QtCore
from PyQt6.QtCore import Qt, QSettings, QSize, QRect, QPoint, QTimer
from PyQt6.QtGui import QPainter, QPen, QPalette, QAction, QActionGroup, QColor, QFont
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QVBoxLayout, 
    QComboBox,      # Added
    QHBoxLayout, 
    QFrame, 
    QLabel,
    QSizePolicy,     # Added - this can be useful for size policies
    QApplication,
    QStyledItemDelegate,  # Add this import
    QWidget,  # Add this import
    QStyle,  # Add this import
    QPushButton,  # Add this import
    QMenu,  # Add this import
    QTextEdit,  # Add this import
    QDialog,  # Add this import
    QVBoxLayout,  # Add this import
    QTextEdit,  # Add this import
    QMessageBox,  # Add this import
    QToolTip  # Add this import
)
from kerykeion import AstrologicalSubject, Report, KerykeionChartSVG
import math
import os
from datetime import datetime

class NorthernChartWidget(QtWidgets.QWidget):
    # Dictionary for zodiac symbols
    ZODIAC_SYMBOLS = {
        'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
        'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
        'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
    }
    
    # Dictionary for planet symbols
    PLANET_SYMBOLS = {
        'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
        'Jupiter': '♃', 'Saturn': '♄', 'Rahu': '☊', 'Ketu': '☋'
    }
    
    # Add aspect configurations
    MAJOR_ASPECTS = {
        'Conjunction': 0,
        'Opposition': 180,
        'Trine': 120,
        'Square': 90,
        'Sextile': 60
    }
    
    # Add Nakshatra dictionary with their degrees
    NAKSHATRAS = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
        'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
        'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
        'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
    ]

    # Add Nakshatra Lords mapping
    NAKSHATRA_LORDS = {
        'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun', 
        'Rohini': 'Moon', 'Mrigashira': 'Mars', 'Ardra': 'Rahu',
        'Punarvasu': 'Jupiter', 'Pushya': 'Saturn', 'Ashlesha': 'Mercury',
        'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
        'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu',
        'Vishakha': 'Jupiter', 'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury',
        'Mula': 'Ketu', 'Purva Ashadha': 'Venus', 'Uttara Ashadha': 'Sun',
        'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
        'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 'Revati': 'Mercury'
    }

    def __init__(self, parent=None, input_page=None):
        super().__init__(parent)
        self.input_page = input_page
        self.chart_data = None
        self.transit_data = None  # Add transit data storage
        self.show_transits = False  # Toggle for transit display
        self.points = None  # Initialize points
        self.houses = None  # Initialize houses
        self.house_cusps = None 
        self.setMinimumSize(500, 500)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.current_nakshatra = None
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create controls container and align right
        self.controls_container = QWidget()
        self.controls_layout = QHBoxLayout(self.controls_container)
        self.controls_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Create Settings Button
        self.settings_button = QPushButton("⚙️ Settings")  # Using gear emoji
        self.settings_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Create Settings Menu
        self.settings_menu = QMenu(self)
        
        # Create Transit Action - Add this before adding to menu
        self.transit_action = QAction("Show Transits", self)
        self.transit_action.setCheckable(True)
        self.transit_action.triggered.connect(self.toggle_transits)
        
        # Planet Style submenu
        self.style_menu = QMenu("Planet Style", self)
        self.style_group = QActionGroup(self)
        self.style_group.setExclusive(True)
        
        for style in ['basic', 'geometric', 'enhanced', 'labeled', 'text']:
            action = QAction(style.capitalize(), self.style_group)
            action.setCheckable(True)
            action.setData(style)
            self.style_menu.addAction(action)
            if style == 'basic':  # Set default
                action.setChecked(True)
        
        # Theme submenu
        self.theme_menu = QMenu("Theme", self)
        self.theme_group = QActionGroup(self)
        self.theme_group.setExclusive(True)
        
        for theme in ['Light', 'Dark', 'Classic']:
            action = QAction(theme, self.theme_group)
            action.setCheckable(True)
            action.setData(theme)
            self.theme_menu.addAction(action)
            if theme == 'Light':  # Set default
                action.setChecked(True)
        
        # Add Horary submenu
        self.horary_menu = QMenu("Horary", self)
        self.horary_group = QActionGroup(self)
        self.horary_group.setExclusive(True)
        
        # Add Yogeswarananda 12 System submenu
        self.yogeswarananda_menu = QMenu("Yogeswarananda 12 System", self)
        self.yogeswarananda_action = QAction("Show Yogeswarananda 12", self)
        self.yogeswarananda_action.triggered.connect(self.show_yogeswarananda)
        self.yogeswarananda_menu.addAction(self.yogeswarananda_action)
        self.horary_menu.addMenu(self.yogeswarananda_menu)
        self.horary_menu.addSeparator()
        
        # Add separator after Yogeswarananda menu
        self.horary_menu.addSeparator()
        
        # Add separator for additional horary options
        self.horary_menu.addSeparator()
        
        # Add additional horary toggles
        self.consideration_action = QAction("Show Considerations", self)
        self.consideration_action.setCheckable(True)
        self.horary_menu.addAction(self.consideration_action)
        
        self.dignity_action = QAction("Show Essential Dignities", self)
        self.dignity_action.setCheckable(True)
        self.horary_menu.addAction(self.dignity_action)
        
        # Add all menus to main settings menu
        self.settings_menu.addMenu(self.style_menu)
        self.settings_menu.addMenu(self.theme_menu)
        self.settings_menu.addMenu(self.horary_menu)  # Add horary menu
        
        # Add Calculation Settings submenu
        self.calc_settings_menu = QMenu("Calculation Settings", self)
        
        # Calculation Type
        self.calc_type_menu = QMenu("Calculation Type", self)
        self.calc_type_group = QActionGroup(self)
        self.calc_type_group.setExclusive(True)
        for calc_type in ["Geocentric", "Topocentric"]:
            action = QAction(calc_type, self.calc_type_group)
            action.setCheckable(True)
            action.setData(calc_type)
            self.calc_type_menu.addAction(action)
            if calc_type == "Geocentric":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.calc_type_menu)
        
        # Zodiac System
        self.zodiac_menu = QMenu("Zodiac System", self)
        self.zodiac_group = QActionGroup(self)
        self.zodiac_group.setExclusive(True)
        for system in ["Tropical", "Sidereal"]:
            action = QAction(system, self.zodiac_group)
            action.setCheckable(True)
            action.setData(system)
            self.zodiac_menu.addAction(action)
            if system == "Sidereal":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.zodiac_menu)
        
        # Ayanamsa (enabled only for Sidereal)
        self.ayanamsa_menu = QMenu("Ayanamsa", self)
        self.ayanamsa_group = QActionGroup(self)
        self.ayanamsa_group.setExclusive(True)
        for ayanamsa in ["Lahiri", "Raman", "Krishnamurti", "Fagan/Bradley", "True Chitrapaksha"]:
            action = QAction(ayanamsa, self.ayanamsa_group)
            action.setCheckable(True)
            action.setData(ayanamsa)
            self.ayanamsa_menu.addAction(action)
            if ayanamsa == "Lahiri":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.ayanamsa_menu)
        
        # House System
        self.house_menu = QMenu("House System", self)
        self.house_group = QActionGroup(self)
        self.house_group.setExclusive(True)
        house_systems = [
            "Placidus", "Koch", "Equal (Asc)", "Equal (MC)", "Whole Sign",
            "Campanus", "Regiomontanus", "Porphyry", "Morinus", "Meridian",
            "Alcabitius", "Azimuthal", "Polich/Page (Topocentric)", "Vehlow Equal"
        ]
        for system in house_systems:
            action = QAction(system, self.house_group)
            action.setCheckable(True)
            action.setData(system)
            self.house_menu.addAction(action)
            if system == "Placidus":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.house_menu)
        
        # Node Type
        self.node_menu = QMenu("Node Type", self)
        self.node_group = QActionGroup(self)
        self.node_group.setExclusive(True)
        for node_type in ["True Node (Rahu/Ketu)", "Mean Node (Rahu/Ketu)"]:
            action = QAction(node_type, self.node_group)
            action.setCheckable(True)
            action.setData(node_type)
            self.node_menu.addAction(action)
            if node_type == "True Node (Rahu/Ketu)":
                action.setChecked(True)
        self.calc_settings_menu.addMenu(self.node_menu)
        
        # Add calculation settings menu and transit action
        self.settings_menu.addMenu(self.calc_settings_menu)
        self.settings_menu.addAction(self.transit_action)
        
        # Connect action groups to handlers
        self.style_group.triggered.connect(self.handle_style_change)
        self.theme_group.triggered.connect(self.handle_theme_change)
        self.horary_group.triggered.connect(self.handle_horary_change)
        self.consideration_action.triggered.connect(self.toggle_considerations)
        self.dignity_action.triggered.connect(self.toggle_dignities)
        self.zodiac_group.triggered.connect(self.handle_zodiac_change)
        self.calc_type_group.triggered.connect(self.handle_calc_type_change)
        self.ayanamsa_group.triggered.connect(self.handle_ayanamsa_change)
        self.house_group.triggered.connect(self.handle_house_change)
        self.node_group.triggered.connect(self.handle_node_change)
        
        # Connect button to menu
        self.settings_button.clicked.connect(self.show_settings_menu)
        
        # Add settings button to controls layout
        self.controls_layout.addWidget(self.settings_button)
        
        # Add controls to main layout at the bottom
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.controls_container)
        
        # Initialize displays with default styles
        self.planet_display = EnhancedPlanetDisplay(style='basic')
        self.current_theme = 'Light'
        
        # Load saved preferences
        self.load_preferences()
        
        # Initialize transit data
        self.transit_data = None
        self.show_transits = False

        # Create container widget for Yogeswarananda display
        self.yogeswarananda_container = QWidget(self)
        self.yogeswarananda_container.setFixedWidth(350)  # Narrower width
        self.yogeswarananda_container.setFixedHeight(600)  # Taller height
        
        # Create layout for container
        container_layout = QVBoxLayout(self.yogeswarananda_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header with close button
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add spacer to push close button to right
        header_layout.addStretch()
        
        # Create close button
        close_button = QPushButton("×")  # Using × symbol
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(lambda: self.yogeswarananda_container.hide())
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 20px;
                color: inherit;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        header_layout.addWidget(close_button)
        
        # Add header to container
        container_layout.addWidget(header)
        
        # Create text display
        self.yogeswarananda_display = QTextEdit()
        self.yogeswarananda_display.setReadOnly(True)
        self.update_yogeswarananda_style()  # Initial style
        
        # Add text display to container
        container_layout.addWidget(self.yogeswarananda_display)
        
        # Position container at bottom left
        self.yogeswarananda_container.move(10, self.height() - 610)
        self.yogeswarananda_container.hide()  # Hidden by default

        # Create custom tooltip
        self.custom_tooltip = CustomTooltip(self)

        # Detailed Nakshatra information for tooltips
        self.nakshatra_info = {
            'Ashwini': '''Deity: Ashwini Kumaras
Attributes: Healing, Speed, New Beginnings
Significance: Represents vitality and health.''',
            'Bharani': '''Deity: Yama
Attributes: Transformation, Duty, Justice
Significance: Governs life and death, and the cycle of rebirth.''',
            'Krittika': '''Deity: Agni
Attributes: Purification, Energy, Passion
Significance: Symbolizes fire and transformation.''',
            'Rohini': '''Deity: Brahma
Attributes: Fertility, Growth, Creativity
Significance: Associated with abundance and nurturing.''',
            'Mriga': '''Deity: Chandra (Moon)
Attributes: Sensitivity, Intuition, Emotion
Significance: Represents the mind and emotional depth.''',
            'Pushya': '''Deity: Brihaspati (Jupiter)
Attributes: Wisdom, Knowledge, Spiritual Growth
Significance: Symbolizes learning and guidance.''',
            'Ashlesha': '''Deity: Naga (Serpent)
Attributes: Mysticism, Intuition, Transformation
Significance: Represents hidden knowledge and secrets.''',
            'Magha': '''Deity: Pitrs (Ancestors)
Attributes: Heritage, Authority, Power
Significance: Governs lineage and ancestral connections.''',
            'Purva Phalguni': '''Deity: Bhaga
Attributes: Pleasure, Enjoyment, Love
Significance: Represents relationships and sensuality.''',
            'Uttara Phalguni': '''Deity: Aryaman
Attributes: Friendship, Support, Loyalty
Significance: Symbolizes partnerships and social connections.''',
            'Hasta': '''Deity: Savitar (Sun)
Attributes: Skill, Craftsmanship, Dexterity
Significance: Represents manual skills and creativity.''',
            'Chitra': '''Deity: Vishvakarma
Attributes: Artistry, Architecture, Creativity
Significance: Symbolizes beauty and artistic expression.''',
            'Swati': '''Deity: Vayu (Wind)
Attributes: Freedom, Independence, Change
Significance: Represents movement and adaptability.''',
            'Vishakha': '''Deity: Indra and Agni
Attributes: Power, Ambition, Success
Significance: Governs achievement and recognition.''',
            'Anuradha': '''Deity: Mitra
Attributes: Friendship, Cooperation, Harmony
Significance: Represents alliances and social bonds.''',
            'Jyeshtha': '''Deity: Indra
Attributes: Leadership, Authority, Protection
Significance: Symbolizes power and dominance.''',
            'Mula': '''Deity: Kali
Attributes: Destruction, Transformation, Rebirth
Significance: Represents the cycle of life and death.''',
            'Purva Ashadha': '''Deity: Apah
Attributes: Water, Purification, Flow
Significance: Symbolizes emotional depth and adaptability.''',
            'Uttara Ashadha': '''Deity: Vishnu
Attributes: Preservation, Protection, Order
Significance: Represents stability and support.''',
            'Shravana': '''Deity: Vishnu
Attributes: Listening, Learning, Communication
Significance: Symbolizes knowledge and understanding.''',
            'Dhanishta': '''Deity: Vasu
Attributes: Wealth, Prosperity, Abundance
Significance: Represents material success and fulfillment.''',
            'Shatabhisha': '''Deity: Varuna
Attributes: Healing, Protection, Mystery
Significance: Governs health and hidden truths.''',
            'Purva Bhadrapada': '''Deity: Aditi
Attributes: Freedom, Expansion, Nurturing
Significance: Represents the cosmic mother and universal love.''',
            'Uttara Bhadrapada': '''Deity: Ahirbudhnya
Attributes: Depth, Mystery, Intuition
Significance: Symbolizes the subconscious and hidden knowledge.''',
            'Revati': '''Deity: Pushan
Attributes: Nourishment, Guidance, Protection
Significance: Represents care and support in life's journey.''',
            'Ardra': '''Deity: Rudra
Attributes: Storm, Effort, Struggle
Significance: Represents power and transformation through hardship.''',
        }

    def handle_zodiac_change(self, action):
        """Handle zodiac system change"""
        zodiac_system = action.data()
        # Enable/disable ayanamsa menu based on zodiac system
        self.ayanamsa_menu.setEnabled(zodiac_system == "Sidereal")
        # Recalculate chart with new settings
        if self.input_page:
            self.input_page.zodiac_system.setCurrentText(zodiac_system)
            self.input_page.calculate_chart()
        else:
            self.recalculate_chart()

    def handle_calc_type_change(self, action):
        """Handle calculation type change"""
        calc_type = action.data()
        # Recalculate chart with new settings
        if self.input_page:
            self.input_page.calc_type.setCurrentText(calc_type)
            self.input_page.calculate_chart()
        else:
            self.recalculate_chart()

    def handle_ayanamsa_change(self, action):
        """Handle ayanamsa change"""
        ayanamsa = action.data()
        # Recalculate chart with new settings
        if self.input_page:
            self.input_page.ayanamsa.setCurrentText(ayanamsa)
            self.input_page.calculate_chart()
        else:
            self.recalculate_chart()

    def handle_house_change(self, action):
        """Handle house system change"""
        house_system = action.data()
        # Recalculate chart with new settings
        if self.input_page:
            self.input_page.house_system.setCurrentText(house_system)
            self.input_page.calculate_chart()
        else:
            self.recalculate_chart()

    def handle_node_change(self, action):
        """Handle node type change"""
        node_type = action.data()
        # Recalculate chart with new settings
        if self.input_page:
            self.input_page.node_type.setCurrentText(node_type)
            self.input_page.calculate_chart()
        else:
            self.recalculate_chart()

    def recalculate_chart(self):
        """Recalculate chart with current settings"""
        if not hasattr(self, 'birth_data'):
            return
            
        # Get current settings
        calc_type = next(action for action in self.calc_type_group.actions() if action.isChecked()).data()
        zodiac = next(action for action in self.zodiac_group.actions() if action.isChecked()).data()
        ayanamsa = next(action for action in self.ayanamsa_group.actions() if action.isChecked()).data()
        house_system = next(action for action in self.house_group.actions() if action.isChecked()).data()
        node_type = next(action for action in self.node_group.actions() if action.isChecked()).data()
        
        # Calculate new chart data
        try:
            from utils.astro_calc import AstroCalc
            astro_calc = AstroCalc()
            new_data = astro_calc.calculate_chart(
                dt=self.birth_data['datetime'],
                lat=self.birth_data['latitude'],
                lon=self.birth_data['longitude'],
                calc_type=calc_type,
                zodiac=zodiac,
                ayanamsa=ayanamsa,
                house_system=house_system,
                node_type=node_type
            )
            self.update_data(new_data)
        except Exception as e:
            print(f"Error recalculating chart: {e}")

    def mouseMoveEvent(self, event):
        """Handle mouse movement to show Nakshatra tooltips"""
        if not hasattr(self, 'points') or not self.points:
            return

        # Get mouse position
        pos = event.pos()
        cx = self.width() // 2
        cy = self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 40

        # Calculate angle from center
        dx = pos.x() - cx
        dy = pos.y() - cy
        angle = math.degrees(math.atan2(-dy, dx)) + 90
        if angle < 0:
            angle += 360

        # Calculate which Nakshatra this corresponds to
        nakshatra_index = int((angle * 27) / 360)
        nakshatra = self.NAKSHATRAS[nakshatra_index]

        # Calculate distance from center
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Only update tooltip if mouse is in the outer ring and nakshatra exists in info
        if (0.85 * radius <= distance <= radius and 
            nakshatra != getattr(self, 'current_nakshatra', None) and 
            nakshatra in self.nakshatra_info):
            
            self.current_nakshatra = nakshatra
            
            # Create tooltip at mouse position, but ensure it stays within window bounds
            tooltip = QToolTip
            tooltip.setFont(QFont('Arial', 10))
            
            # Get screen geometry to handle tooltip positioning
            screen = QApplication.primaryScreen().geometry()
            global_pos = self.mapToGlobal(pos)
            
            # Show tooltip slightly offset from cursor
            tooltip_pos = QPoint(global_pos.x() + 15, global_pos.y() + 15)
            
            # Ensure tooltip stays within screen bounds
            if tooltip_pos.x() + 350 > screen.right():  # Assuming tooltip width of 350px
                tooltip_pos.setX(global_pos.x() - 365)  # Move to left of cursor
            if tooltip_pos.y() + 200 > screen.bottom():  # Assuming tooltip height of 200px
                tooltip_pos.setY(global_pos.y() - 215)  # Move above cursor
            
            tooltip.showText(tooltip_pos, self.nakshatra_info[nakshatra])

    def update_yogeswarananda_style(self):
        """Update Yogeswarananda display style based on current theme"""
        text_color = self.current_theme['text'].name()  # Get color from current theme
        self.yogeswarananda_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                color: {text_color};
                border: none;
                font-family: monospace;
                font-size: 16px;  /* Larger font size */
                line-height: 1.8;  /* Increased line spacing */
            }}
        """)
        # Enable rich text interpretation
        self.yogeswarananda_display.setHtml(self.yogeswarananda_display.toPlainText())

    def show_settings_menu(self):
        """Show the settings menu below the settings button"""
        self.settings_menu.popup(self.settings_button.mapToGlobal(
            QPoint(0, self.settings_button.height())))

    def handle_style_change(self, action):
        """Handle planet style change from menu"""
        style = action.data()
        self.change_planet_style(style)
        self.save_preferences()

    def handle_theme_change(self, action):
        """Handle theme change from menu"""
        theme = action.data()
        self.change_theme(theme)
        self.update_yogeswarananda_style()  # Update text display style when theme changes
        self.save_preferences()
        
        # Update nakshatra info with new theme colors
        self.update_nakshatra_info()
        
        self.update()

    def handle_horary_change(self, action):
        """Handle horary style change from menu"""
        option = action.data()
        print(f"Changing horary style to: {option}")
        
        # Store the selected horary style
        self.current_horary_style = option
        
        # Update display based on horary style
        if option == 'Traditional Rules':
            self.apply_traditional_rules()
        elif option == 'Modern Adaptation':
            self.apply_modern_adaptation()
        elif option == 'Simplified':
            self.apply_simplified_rules()
        elif option == 'Advanced Analysis':
            self.apply_advanced_analysis()
        
        self.update()  # Redraw the chart

    def save_preferences(self):
        """Save current chart preferences"""
        settings = QSettings('YourCompany', 'AstrologyApp')
        
        # Save planet style
        checked_style = next(action for action in self.style_group.actions() 
                            if action.isChecked())
        settings.setValue('planet_style', checked_style.data())
        
        # Save theme
        checked_theme = next(action for action in self.theme_group.actions() 
                            if action.isChecked())
        settings.setValue('chart_theme', checked_theme.data())

    def load_preferences(self):
        """Load saved chart preferences"""
        settings = QSettings('YourCompany', 'AstrologyApp')
        
        # Load planet style
        style = settings.value('planet_style', 'basic')
        for action in self.style_group.actions():
            if action.data() == style:
                action.setChecked(True)
                self.change_planet_style(style)
                break
        
        # Load theme
        theme = settings.value('chart_theme', 'Light')
        for action in self.theme_group.actions():
            if action.data() == theme:
                action.setChecked(True)
                self.change_theme(theme)
                break

    def change_planet_style(self, style):
        """Change the planet display style"""
        print(f"\nDEBUG - Changing planet style to: {style}")
        self.planet_display = EnhancedPlanetDisplay(style=style, points=self.points)
        print(f"New planet_display style: {self.planet_display.style}")
        self.update()  # Redraw the chart

    def update_data(self, chart_data):
        """Update the chart with new data"""
        print("\nDEBUG - update_data called with:", type(chart_data))
        try:
            # Store the data
            self.chart_data = chart_data
            
            # Extract points and houses directly from the dictionary
            if isinstance(chart_data, dict):
                print("Processing chart data dictionary...")
                # Get points including Ascendant
                self.points = {}
                for point_name, point_data in chart_data.get('points', {}).items():
                    print(f"Processing point: {point_name}")
                    # Include Ascendant and all planets except outer planets
                    if point_name == 'Ascendant' or point_name in self.PLANET_SYMBOLS:
                        print(f"Adding {point_name} to points dictionary")
                        self.points[point_name] = {
                            'longitude': point_data['longitude'],
                            'sign': point_data['sign'],
                            'degree': point_data['degree'],
                            'is_retrograde': point_data.get('is_retrograde', False)
                        }
                
                # Store the full houses data
                self.houses = chart_data.get('houses', {})
                
                # Get house cusps as a list using exact longitudes
                self.house_cusps = [
                    float(chart_data['houses'][f'House_{i}']['longitude'])
                    for i in range(1, 13)
                ]
                
                # Debug prints
                print("\nDEBUG - Chart Widget Points:")
                print("Points:", self.points)
                print("House cusps:", self.house_cusps)
                print(f"Number of planets: {len(self.points)}")
                
                # Update Yogeswarananda display if data exists
                if isinstance(chart_data, dict) and 'yogeswarananda_12' in chart_data:
                    yogeswarananda_data = chart_data['yogeswarananda_12']
                    text = "Yogeswarananda 12 System:\n"
                    text += "------------------------\n"
                    for k, v in yogeswarananda_data.items():
                        text += f"{k}: {v}\n"
                    self.yogeswarananda_display.setText(text)
                    self.yogeswarananda_container.show()
                else:
                    self.yogeswarananda_container.hide()
                
                self.update()  # Trigger repaint
            else:
                print(f"Error: chart_data is not a dictionary: {type(chart_data)}")
                
        except Exception as e:
            print(f"Error updating chart: {str(e)}")
            import traceback
            traceback.print_exc()  # This will print the full error traceback

    def calculate_scale_factors(self, radius):
        """Calculate scaling factors based on chart radius"""
        self.scale = {
            'symbol_size': int(radius * 0.06),     # Zodiac symbols
            'name_size': int(radius * 0.04),       # Zodiac names
            'planet_size': int(radius * 0.15),     # Planet size
            'nakshatra_size': int(radius * 0.03),  # Nakshatra text
            'degree_size': int(radius * 0.06),     # Degree text
            'line_width': max(1, int(radius * 0.004)),
            'text_margin': int(radius * 0.02),
            
            # Ring radii
            'outer_ring': 0.85,        # Purple ring (Zodiac)
            'middle_ring': 0.85,      # Purple ring (Zodiac)
            'inner_ring': 0.7,        # Yellow ring (Planets)
            'center_ring': 0.25,      # Inner circle
            
            # Different radii for text vs symbol modes
            'planet_radius': 1,    # Add this line - general planet radius
            'planet_radius_text': 0.85,     # Radius when in text mode
            'planet_radius_symbol': 0.55,   # Radius when in symbol mode
            'transit_radius_text': 0.72,    # Transit radius in text mode
            'transit_radius_symbol': 0.52,  # Transit radius in symbol mode
            'zodiac_radius': 0.925,         # Keep the same
            'nakshatra_radius': 0.96        # Keep the same
        }
        return self.scale

    def draw_zodiac_symbols(self, painter, cx, cy, radius):
        """Draw zodiac symbols and names with relative scaling"""
        scale = self.calculate_scale_factors(radius)
        
        # Set up fonts with relative sizes
        symbol_font = QtGui.QFont()
        symbol_font.setPointSize(scale['symbol_size'])
        name_font = QtGui.QFont()
        name_font.setPointSize(scale['name_size'])
        name_font.setBold(True)
        
        painter.setPen(self.current_theme['text'])
        
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer',
                 'Leo', 'Virgo', 'Libra', 'Scorpio',
                 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        for i, sign in enumerate(signs):
            angle = 270 - (i * 30)
            mid_angle = angle - 15
            angle_rad = math.radians(-mid_angle)
            
            x = cx + radius * scale['zodiac_radius'] * math.cos(angle_rad)
            y = cy - radius * scale['zodiac_radius'] * math.sin(angle_rad)
            
            painter.save()
            painter.translate(x, y)
            text_angle = mid_angle - 90
            if text_angle > 90 or text_angle < -90:
                text_angle += 180
            painter.rotate(text_angle)
            
            # Convert all coordinates and dimensions to integers
            box_size = int(scale['symbol_size'] * 2)
            name_height = int(scale['name_size'] * 1.5)
            text_margin = int(scale['text_margin'])
            
            painter.setFont(symbol_font)
            symbol = self.ZODIAC_SYMBOLS[sign]
            painter.drawText(int(-box_size/2), int(-box_size/2), box_size, box_size,
                            Qt.AlignmentFlag.AlignCenter, symbol)
            
            painter.setFont(name_font)
            painter.drawText(int(-box_size), text_margin,
                            box_size * 2, name_height,
                            Qt.AlignmentFlag.AlignCenter, sign)
            painter.restore()

    def draw_house_lines(self, painter, cx, cy, radius):
        """Draw house lines in the purple zodiac ring"""
        scale = self.calculate_scale_factors(radius)
        painter.setPen(QPen(self.current_theme['houses'], scale['line_width']))
        
        for i in range(12):
            angle = 270 - (i * 30)
            angle_rad = math.radians(-angle)
            
            # Start and end points for purple ring lines
            x1 = cx + radius * 1.0 * math.cos(angle_rad)      # Outer edge
            y1 = cy - radius * 1.0 * math.sin(angle_rad)
            x2 = cx + radius * 0.83 * math.cos(angle_rad)     # Inner edge of purple ring
            y2 = cy - radius * 0.83 * math.sin(angle_rad)
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def draw_planets(self, painter, cx, cy, radius):
        """Draw either natal or transit planets based on toggle"""
        print(f"\nDEBUG - draw_planets called")
        print(f"Show transits: {self.show_transits}")
        print(f"Has transit data: {self.transit_data is not None}")
        
        scale = self.calculate_scale_factors(radius)
        
        if self.show_transits and self.transit_data:
            # Only draw transit planets when toggle is on
            print("Drawing transit planets only")
            self.draw_planet_set(painter, cx, cy, radius, self.transit_data, scale, is_transit=True)
        else:
            # Draw natal planets when toggle is off
            if self.points:
                print("Drawing natal planets")
                self.draw_planet_set(painter, cx, cy, radius, self.points, scale, is_transit=False)
            else:
                print("No natal points available")

    def draw_planet_set(self, painter, cx, cy, radius, points, scale, is_transit=False):
        """Draw a set of planets (either natal or transit)"""
        # Group planets by proximity
        proximity_threshold = 15
        planet_groups = self.group_planets_by_proximity(points, proximity_threshold)
        
        # Choose radius based on style and transit status
        if self.planet_display.style == 'text':
            base_radius = radius * (scale['transit_radius_text'] if is_transit else scale['planet_radius_text'])
        else:
            base_radius = radius * (scale['transit_radius_symbol'] if is_transit else scale['planet_radius_symbol'])
        
        for group in planet_groups:
            if len(group) == 1:
                planet_name = group[0]
                if is_transit and planet_name == 'Ascendant':
                    continue
                self.draw_single_planet(painter, cx, cy, base_radius, planet_name, 
                                     points[planet_name], scale, is_transit)
            else:
                if is_transit:
                    group = [p for p in group if p != 'Ascendant']
                    if not group:
                        continue
                self.draw_planet_group(painter, cx, cy, base_radius, group, scale, is_transit)

    def draw_single_planet(self, painter, cx, cy, radius, planet_name, planet_data, scale, is_transit=False):
        """Draw a single planet with transit modifications if needed"""
        angle_rad = math.radians(90 + planet_data['longitude'])
        radius_scaled = radius * scale['planet_radius']
        
        x = cx + radius_scaled * math.cos(angle_rad)
        y = cy - radius_scaled * math.sin(angle_rad)

        # Modify appearance for transit planets
        if is_transit:
            # Use different style for transit planets
            transit_style = 'text' if self.planet_display.style == 'text' else 'basic'
            transit_display = EnhancedPlanetDisplay(style=transit_style)
            
            # Draw transit symbol with modifications
            painter.save()
            painter.setPen(QPen(QtGui.QColor(100, 100, 100)))  # Lighter color for transits
            transit_display.draw_planet(painter, planet_name, int(x), int(y), 
                                     int(scale['planet_size'] * 0.8))  # Slightly smaller
            painter.restore()
        else:
            # Draw natal planet normally
            self.planet_display.draw_planet(painter, planet_name, int(x), int(y), 
                                         int(scale['planet_size']))

    def draw_planet_group(self, painter, cx, cy, radius, group, scale, is_transit=False):
        """Draw a group of planets with adjusted spacing"""
        if len(group) == 1:
            planet_name = group[0]
            self.draw_single_planet(painter, cx, cy, radius, planet_name, 
                                  self.points[planet_name], scale, is_transit)
        else:
            # Adjust radius step based on display style
            if self.planet_display.style == 'text':
                radius_step = scale['planet_size'] * 0.4  # Smaller step for text mode
            else:
                radius_step = scale['planet_size'] * 0.8  # Larger step for symbol mode
            
            for i, planet_name in enumerate(group):
                adjusted_radius = radius - (i * radius_step)
                longitude = self.points[planet_name]['longitude']
                angle_rad = math.radians(90 + longitude)
                x = cx + adjusted_radius * math.cos(angle_rad)
                y = cy - adjusted_radius * math.sin(angle_rad)
                
                self.planet_display.draw_planet(painter, planet_name, int(x), int(y), 
                                         scale['planet_size'])

    def draw_nakshatras(self, painter, cx, cy, radius):
        """Draw nakshatra names with larger font"""
        scale = self.calculate_scale_factors(radius)
        
        # Define short names for nakshatras - simplified version
        SHORT_NAMES = {
            'Ashwini': 'Ashwini', 'Bharani': 'Bharani', 'Krittika': 'Krittika',
            'Rohini': 'Rohini', 'Mrigashira': 'Mrigashira', 'Ardra': 'Ardra',
            'Punarvasu': 'Punarvasu', 'Pushya': 'Pushya', 'Ashlesha': 'Ashlesha',
            'Magha': 'Magha', 'Purva Phalguni': 'P Phalguni', 'Uttara Phalguni': 'U Phalguni',
            'Hasta': 'Hasta', 'Chitra': 'Chitra', 'Swati': 'Swati',
            'Vishakha': 'Vishakha', 'Anuradha': 'Anuradha', 'Jyeshtha': 'Jyeshtha',
            'Mula': 'Mula', 'Purva Ashadha': 'P Ashadha', 'Uttara Ashadha': 'U Ashadha',
            'Shravana': 'Shravana', 'Dhanishta': 'Dhanishta', 'Shatabhisha': 'Shatabhisha',
            'Purva Bhadrapada': 'P Bhadrapada', 'Uttara Bhadrapada': 'U Bhadrapada', 'Revati': 'Revati'
        }
        
        nakshatra_font = QtGui.QFont()
        nakshatra_font.setPointSize(int(scale['nakshatra_size']))
        
        # Create a smaller font for the lords
        lord_font = QtGui.QFont()
        lord_font.setPointSize(int(scale['nakshatra_size'] * 0.8))  # 80% of nakshatra name size
        
        painter.setPen(self.current_theme['text'])
        
        nakshatra_degrees = 360 / 27
        
        for i, nakshatra in enumerate(self.NAKSHATRAS):
            angle = 270 - (i * nakshatra_degrees)
            mid_angle = angle - (nakshatra_degrees / 2)
            angle_rad = math.radians(-mid_angle)
            
            x = cx + radius * scale['nakshatra_radius'] * math.cos(angle_rad)
            y = cy - radius * scale['nakshatra_radius'] * math.sin(angle_rad)
            
            painter.save()
            painter.translate(x, y)
            text_angle = mid_angle - 90
            if text_angle > 90 or text_angle < -90:
                text_angle += 180
            painter.rotate(text_angle)
            
            # Use shorter text
            short_name = SHORT_NAMES[nakshatra]
            lord_name = self.NAKSHATRA_LORDS[nakshatra]
            
            # Create larger bounding box to accommodate both texts
            box_width = scale['nakshatra_size'] * 6
            box_height = scale['nakshatra_size'] * 3  # Increased height for two lines
            
            # Create rectangle with larger dimensions
            text_rect = QtCore.QRectF(
                -box_width/2,
                -box_height/2,
                box_width,
                box_height
            )
            
            # Draw nakshatra name
            painter.setFont(nakshatra_font)
            painter.setPen(self.current_theme['text'])  # Regular text color for nakshatra name
            name_rect = QtCore.QRectF(
                -box_width/2,
                -box_height/2,
                box_width,
                box_height/2
            )
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, short_name)
            
            # Draw lord name
            painter.setFont(lord_font)
            painter.setPen(self.current_theme['nakshatra_lord'])  # Green color for lord name
            lord_rect = QtCore.QRectF(
                -box_width/2,
                0,  # Start from middle of box
                box_width,
                box_height/2
            )
            painter.drawText(lord_rect, Qt.AlignmentFlag.AlignCenter, lord_name)
            
            painter.restore()

    def draw_nakshatra_lines(self, painter, cx, cy, radius):
        """Draw nakshatra division lines in green ring"""
        painter.setPen(QPen(self.current_theme['text'], 1))
        
        # Each nakshatra is exactly 13.333... degrees
        nakshatra_degrees = 360 / 27
        
        for i in range(27):
            # Start from 270° (top/Aries) and go counterclockwise
            angle = 270 - (i * nakshatra_degrees)
            angle_rad = math.radians(-angle)
            
            # Draw lines in green ring only
            x1 = cx + radius * math.cos(angle_rad)        # Outer edge
            y1 = cy - radius * math.sin(angle_rad)
            x2 = cx + radius * 0.85 * math.cos(angle_rad) # Inner edge of purple ring
            y2 = cy - radius * 0.85 * math.sin(angle_rad)
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def draw_house_cusps(self, painter, cx, cy, radius):
        """Draw house cusp lines and Roman numeral numbers near the periphery"""
        try:
            if not hasattr(self, 'house_cusps') or not self.house_cusps:
                return
            
            # Roman numeral conversion dictionary
            ROMAN_NUMERALS = {
                1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI',
                7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'
            }
            
            scale = self.calculate_scale_factors(radius)
            
            # Define the spans
            outer_span = 0.83
            inner_span = 0.30
            
            # Move numbers closer to periphery (increased from previous value)
            number_radius = radius * 0.80  # Increased to move numbers outward
            
            # Use theme color
            cusp_pen = QPen(self.current_theme['houses'])
            cusp_pen.setWidth(1)
            painter.setPen(cusp_pen)
            
            # Set up font for house numbers with larger size
            font = QtGui.QFont('Arial', int(radius * 0.04))  # Increased from 0.035
            font.setWeight(QtGui.QFont.Weight.ExtraBold)
            font.setLetterSpacing(QtGui.QFont.SpacingType.AbsoluteSpacing, 1)
            painter.setFont(font)
            
            # Draw lines and numbers for each house
            for i in range(12):
                # Get current and next cusp angles
                current_cusp = float(self.house_cusps[i])
                next_cusp = float(self.house_cusps[(i + 1) % 12])
                
                # Handle case where house crosses 0°
                if next_cusp < current_cusp:
                    next_cusp += 360
                
                # Calculate middle of the house
                mid_angle = (current_cusp + next_cusp) / 2
                if mid_angle > 360:
                    mid_angle -= 360
                    
                # Draw cusp line
                angle_rad = math.radians(90 + current_cusp)
                x1 = cx + radius * inner_span * math.cos(angle_rad)
                y1 = cy - radius * inner_span * math.sin(angle_rad)
                x2 = cx + radius * outer_span * math.cos(angle_rad)
                y2 = cy - radius * outer_span * math.sin(angle_rad)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                
                # Calculate position for house number
                mid_angle_rad = math.radians(90 + mid_angle)
                num_x = cx + number_radius * math.cos(mid_angle_rad)
                num_y = cy - number_radius * math.sin(mid_angle_rad)
                
                # Create rectangle for text
                text_width = radius * 0.07  # Slightly smaller text box
                text_rect = QtCore.QRectF(
                    num_x - text_width/2,
                    num_y - text_width/2,
                    text_width,
                    text_width
                )
                
                # Draw Roman numeral
                house_number = i + 1
                roman_numeral = ROMAN_NUMERALS[house_number]
                
                # Save current state
                painter.save()
                
                # Translate to number position and rotate text
                painter.translate(num_x, num_y)
                text_angle = mid_angle
                if 90 < text_angle < 270:
                    text_angle += 180
                painter.rotate(-text_angle)
                
                # Draw the text
                new_rect = QtCore.QRectF(-text_width/2, -text_width/2, text_width, text_width)
                
                # Draw text with slight offset for shadow effect
                shadow_color = QColor(0, 0, 0, 100) if self.current_theme == self.themes['Light'] else QColor(255, 255, 255, 100)
                painter.setPen(shadow_color)
                shadow_rect = QtCore.QRectF(-text_width/2 + 1, -text_width/2 + 1, text_width, text_width)
                painter.drawText(shadow_rect, Qt.AlignmentFlag.AlignCenter, roman_numeral)
                
                # Draw main text
                painter.setPen(self.current_theme['house_numbers'])
                painter.drawText(new_rect, Qt.AlignmentFlag.AlignCenter, roman_numeral)
                
                # Restore state
                painter.restore()
                
        except Exception as e:
            print(f"Error in draw_house_cusps: {str(e)}")
            import traceback
            traceback.print_exc()

    def paintEvent(self, event):
        """Draw the chart with planets appearing above the lines"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set background color from theme
        painter.fillRect(self.rect(), self.current_theme['background'])
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        cx = width // 2
        cy = height // 2
        radius = min(width, height) // 2 - 40
        
        # Define ring radii
        outer_radius = radius        # Green ring (Nakshatras)
        middle_radius = radius * 0.85  # Purple ring (Zodiac signs)
        inner_radius = radius * 0.7   # Yellow ring (Planets)
        center_radius = radius * 0.25  # Inner circle
        
        # Create colors with transparency
        green_color = QtGui.QColor(200, 255, 200, 100)   # Light green
        purple_color = QtGui.QColor(230, 200, 255, 100)  # Light purple
        yellow_color = QtGui.QColor(255, 255, 200, 100)  # Light yellow
        
        # Draw rings
        painter.fillPath(self.create_ring_path(cx, cy, outer_radius, middle_radius), green_color)
        painter.fillPath(self.create_ring_path(cx, cy, middle_radius, inner_radius), purple_color)
        painter.fillPath(self.create_ring_path(cx, cy, inner_radius, center_radius), yellow_color)
        
        # Draw circle borders
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        for r in [outer_radius, middle_radius, inner_radius, center_radius]:
            r_int = int(r)
            x_int = int(cx - r_int)
            y_int = int(cy - r_int)
            w_int = int(r_int * 2)
            h_int = int(r_int * 2)
            painter.drawEllipse(x_int, y_int, w_int, h_int)
        
        # Draw divisions and text
        self.draw_nakshatra_lines(painter, cx, cy, outer_radius)
        self.draw_nakshatras(painter, cx, cy, outer_radius)
        self.draw_zodiac_symbols(painter, cx, cy, middle_radius)
        
        # Draw house lines and cusps BEFORE planets
        self.draw_house_lines(painter, cx, cy, middle_radius)
        self.draw_house_cusps(painter, cx, cy, middle_radius)
        
        # Draw planets LAST so they appear on top
        if hasattr(self, 'points') and self.points:
            self.draw_planets(painter, cx, cy, inner_radius)
        
        # Add the text overlay
        self.draw_chart_text(painter)

    def create_ring_path(self, cx, cy, outer_r, inner_r):
        """Helper method to create ring paths"""
        outer = QtGui.QPainterPath()
        outer.addEllipse(cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2)
        inner = QtGui.QPainterPath()
        inner.addEllipse(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)
        return outer - inner

    def draw_planets_with_arrows(self, painter, cx, cy, radius):
        """Draw planets with arrows pointing to their exact positions"""
        if not self.points:
            return
        
        scale = self.calculate_scale_factors(radius)
        
        for planet_name, planet_data in self.points.items():
            if 'longitude' not in planet_data:
                continue
            
            # Log the original longitude
            longitude = float(planet_data['longitude'])
            print(f"{planet_name} original longitude: {longitude}")
            
            # Adjust for 0° Aries at 12 o'clock
            angle_rad = math.radians(-longitude + 90)
            print(f"{planet_name} adjusted angle (radians): {angle_rad}")
            
            # Calculate position for the planet symbol
            x = cx + radius * 0.7 * math.cos(angle_rad)
            y = cy + radius * 0.7 * math.sin(angle_rad)
            print(f"{planet_name} position: ({x}, {y})")
            
            # Draw arrow pointing to the exact degree
            arrow_x = cx + radius * 0.6 * math.cos(angle_rad)
            arrow_y = cy + radius * 0.6 * math.sin(angle_rad)
            painter.drawLine(int(arrow_x), int(arrow_y), int(x), int(y))
            
            # Draw planet symbol
            painter.save()
            painter.translate(x, y)
            
            # Rotate text for readability
            text_angle = -longitude + 90
            if 90 < text_angle < 270:
                text_angle += 180
            painter.rotate(-text_angle)
            
            # Draw planet name
            font = QtGui.QFont('Arial', int(scale['planet_size'] * 0.35))
            painter.setFont(font)
            text = self.PLANET_SYMBOLS.get(planet_name, planet_name)
            painter.drawText(-20, -10, 40, 20, Qt.AlignmentFlag.AlignCenter, text)
            
            # Draw degree
            if 'degree' in planet_data:
                degree_text = f"{planet_data['degree']:.1f}°"
                painter.setFont(QtGui.QFont('Arial', int(scale['planet_size'] * 0.3)))
                painter.drawText(-20, 5, 40, 20, Qt.AlignmentFlag.AlignCenter, degree_text)
            
            painter.restore()

    def draw_chart_text(self, painter):
        """Draw text information around the chart without affecting the chart itself"""
        width = self.width()
        height = self.height()
        
        # Set up font and color
        font = QtGui.QFont('Arial', 9)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.white)
        
        # Left side text
        left_x = 10
        top_y = 30
        
        # Check if self.points exists and is not None
        if hasattr(self, 'points') and self.points is not None:
            for planet, data in self.points.items():
                if planet != 'Ascendant':
                    text = f"{planet}: {data['longitude']:.2f}° {data['sign']}"
                    painter.drawText(left_x, top_y, text)
                    top_y += 20
        
        # Right side text
        right_x = width - 200
        top_y = 30
        
        # Check if self.houses exists and is not None
        if hasattr(self, 'houses') and self.houses is not None:
            for i, (house, data) in enumerate(self.houses.items(), 1):
                text = f"House {i}: {data['longitude']:.2f}° {data['sign']}"
                painter.drawText(right_x, top_y, text)
                top_y += 20

    def change_theme(self, theme):
        """Change the chart's color theme"""
        self.themes = {
            'Dark': {
                'background': QColor(25, 0, 40),  # Darker purple background
                'rings': QColor(128, 0, 128),
                'text': QColor(255, 255, 255),
                'houses': QColor(128, 128, 128),
                'planet_ring': QColor(255, 255, 180),
                'panel_text': QColor(255, 255, 255),
                'panel_background': QColor(0, 0, 0),
                'nakshatra_lord': QColor(144, 238, 144),
                'house_numbers': QColor(255, 255, 255, 230),
            },
            'Light': {
                'background': QColor(255, 255, 255),
                'rings': QColor(128, 0, 128),
                'text': QColor(0, 0, 0),
                'houses': QColor(100, 100, 100),
                'planet_ring': QColor(255, 223, 0),
                'panel_text': QColor(0, 0, 0),
                'panel_background': QColor(240, 240, 240),
                'nakshatra_lord': QColor(34, 139, 34),
                'house_numbers': QColor(0, 0, 0, 230),
            },
            'Classic': {
                'background': QColor(0, 0, 0),  # Black background for classic theme
                'rings': QColor(255, 255, 255),
                'text': QColor(255, 255, 255),
                'houses': QColor(200, 200, 200),
                'planet_ring': QColor(255, 255, 180),
                'panel_text': QColor(255, 255, 255),
                'panel_background': QColor(50, 50, 50),
                'nakshatra_lord': QColor(144, 238, 144),
                'house_numbers': QColor(255, 255, 255, 230),
            }
        }
        
        # Set the current theme
        self.current_theme = self.themes.get(theme, self.themes['Dark'])
        print(f"Theme changed to: {theme}")
        
        # Update side panel colors if it exists
        if hasattr(self, 'side_panel'):
            # Update side panel stylesheet
            self.side_panel.setStyleSheet(f"""
                QWidget {{
                    background-color: {self.current_theme['panel_background'].name()};
                    color: {self.current_theme['panel_text'].name()};
                }}
                QLabel {{
                    color: {self.current_theme['panel_text'].name()};
                }}
                QPushButton {{
                    color: {self.current_theme['panel_text'].name()};
                    background-color: {self.current_theme['houses'].name()};
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: {self.current_theme['rings'].name()};
                }}
                QComboBox {{
                    color: {self.current_theme['panel_text'].name()};
                    background-color: {self.current_theme['houses'].name()};
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }}
                QComboBox QAbstractItemView {{
                    color: {self.current_theme['panel_text'].name()};
                    background-color: {self.current_theme['panel_background'].name()};
                    selection-background-color: {self.current_theme['rings'].name()};
                }}
            """)
        
        # Force a repaint
        self.update()
        
        # Update nakshatra info with new theme colors
        self.update_nakshatra_info()
        
        # Update tooltip theme if it exists
        if hasattr(self, 'custom_tooltip'):
            self.custom_tooltip.set_theme(theme)

    def update_nakshatra_info(self):
        """Update nakshatra info with enhanced HTML formatting"""
        # Determine if we're in dark theme
        is_dark_theme = getattr(self, 'current_theme', {}).get('background', QColor('#FFFFFF')).lightness() < 128
        
        # Set colors based on theme
        if is_dark_theme:
            bg_color = "#2D2D2D"
            text_color = "#FFFFFF"
            border_color = "#404040"
            deity_color = "#90CAF9"  # Light blue
            attr_color = "#A5D6A7"   # Light green
            sig_color = "#FFCC80"    # Light orange
        else:
            bg_color = "#FFFFFF"
            text_color = "#000000"
            border_color = "#DDDDDD"
            deity_color = "#1976D2"  # Darker blue
            attr_color = "#388E3C"   # Darker green
            sig_color = "#F57C00"    # Darker orange

        # Base CSS for tooltip
        base_style = f"""
            <style>
                .tooltip-container {{
                    font-family: Arial, sans-serif;
                    padding: 15px;
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    min-width: 300px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                }}
                .deity {{
                    color: {deity_color};
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid {border_color};
                }}
                .attributes {{
                    color: {attr_color};
                    font-size: 14px;
                    margin: 8px 0;
                    padding-left: 20px;
                }}
                .significance {{
                    color: {sig_color};
                    font-size: 14px;
                    margin: 8px 0;
                    padding-left: 20px;
                }}
                .icon {{
                    display: inline-block;
                    width: 20px;
                    text-align: center;
                    margin-right: 5px;
                }}
            </style>"""

        # Update nakshatra info dictionary with new HTML formatting
        self.nakshatra_info = {
            'Ashwini': f"""{base_style}
                <div class="tooltip-container">
                    <div class="deity">
                        <span class="icon">✨</span> Deity: Ashwini Kumaras
                    </div>
                    <div class="attributes">
                        <span class="icon">🔮</span> Attributes: Healing, Speed, New Beginnings
                    </div>
                    <div class="significance">
                        <span class="icon">🌟</span> Significance: Represents vitality and health.
                    </div>
                </div>""",
            'Bharani': f"""{base_style}
                <div class="tooltip-container">
                    <div class="deity">
                        <span class="icon">✨</span> Deity: Yama
                    </div>
                    <div class="attributes">
                        <span class="icon">🔮</span> Attributes: Transformation, Duty, Justice
                    </div>
                    <div class="significance">
                        <span class="icon">🌟</span> Significance: Governs life and death, and the cycle of rebirth.
                    </div>
                </div>""",
            # ... Add similar formatting for all other Nakshatras ...
            'Ardra': f"""{base_style}
                <div class="tooltip-container">
                    <div class="deity">
                        <span class="icon">✨</span> Deity: Rudra
                    </div>
                    <div class="attributes">
                        <span class="icon">🔮</span> Attributes: Storm, Effort, Struggle
                    </div>
                    <div class="significance">
                        <span class="icon">🌟</span> Significance: Represents power and transformation through hardship.
                    </div>
                </div>"""
        }

    def update_data(self, chart_data):
        """Update the chart with new data"""
        print("\nDEBUG - update_data called with:", type(chart_data))
        try:
            # Store the data
            self.chart_data = chart_data
            
            # Extract points and houses directly from the dictionary
            if isinstance(chart_data, dict) and 'points' in chart_data:
                print("Processing chart data dictionary...")
                # Initialize points dictionary
                self.points = {}
                
                # Process points data
                points_data = chart_data['points']
                for point_name, point_data in points_data.items():
                    print(f"Processing point: {point_name}")
                    # Include Ascendant and all planets except outer planets
                    if point_name == 'Ascendant' or point_name in self.PLANET_SYMBOLS:
                        print(f"Adding {point_name} to points dictionary")
                        self.points[point_name] = point_data.copy()  # Make a copy of the data
                
                # Store the full houses data
                self.houses = chart_data.get('houses', {})
                
                # Get house cusps as a list using exact longitudes
                self.house_cusps = [
                    float(chart_data['houses'][f'House_{i}']['longitude'])
                    for i in range(1, 13)
                ]
                
                # Debug prints
                print("\nDEBUG - Chart Widget Points:")
                print("Points:", self.points)
                print("House cusps:", self.house_cusps)
                print(f"Number of planets: {len(self.points)}")
                
                # Update Yogeswarananda display if data exists
                if isinstance(chart_data, dict) and 'yogeswarananda_12' in chart_data:
                    yogeswarananda_data = chart_data['yogeswarananda_12']
                    text = "Yogeswarananda 12 System:\n"
                    text += "------------------------\n"
                    for k, v in yogeswarananda_data.items():
                        text += f"{k}: {v}\n"
                    self.yogeswarananda_display.setText(text)
                    self.yogeswarananda_container.show()
                else:
                    self.yogeswarananda_container.hide()
                
                self.update()  # Trigger repaint
            else:
                print(f"Error: Invalid chart data format")
                print(f"chart_data keys: {chart_data.keys() if isinstance(chart_data, dict) else 'not a dict'}")
                
        except Exception as e:
            print(f"Error updating chart: {str(e)}")
            import traceback
            traceback.print_exc()

    # Add a method to check widget visibility
    def showEvent(self, event):
        super().showEvent(event)
        print("\nWidget shown:")
        print(f"- Widget size: {self.size()}")
        print(f"- Controls container visible: {self.controls_container.isVisible()}")
        print(f"- Settings button visible: {self.settings_button.isVisible()}")

    def draw_base_chart(self, painter, cx, cy, radius):
        """Draw the base chart elements"""
        # Calculate scale factors
        scale = self.calculate_scale_factors(radius)
        
        # Set up colors based on current theme
        if self.current_theme == 'Dark':
            bg_color = QtGui.QColor(30, 30, 30)
            ring_color = QtGui.QColor(60, 60, 60)
            line_color = QtGui.QColor(100, 100, 100)
        elif self.current_theme == 'Classic':
            bg_color = QtGui.QColor(255, 248, 220)  # Cornsilk
            ring_color = QtGui.QColor(210, 180, 140)  # Tan
            line_color = QtGui.QColor(139, 69, 19)    # Saddle Brown
        else:  # Light theme
            bg_color = QtGui.QColor(255, 255, 255)
            ring_color = QtGui.QColor(240, 240, 240)
            line_color = QtGui.QColor(200, 200, 200)
        
        # Fill background
        painter.fillRect(0, 0, self.width(), self.height(), bg_color)
        
        # Draw outer circle (zodiac ring)
        painter.setPen(QPen(line_color, scale['line_width']))
        painter.setBrush(QtGui.QBrush(ring_color))
        painter.drawEllipse(
            cx - radius,
            cy - radius,
            radius * 2,
            radius * 2
        )
        
        # Draw middle circle (planet ring)
        painter.drawEllipse(
            cx - radius * scale['middle_ring'],
            cy - radius * scale['middle_ring'],
            radius * scale['middle_ring'] * 2,
            radius * scale['middle_ring'] * 2
        )
        
        # Draw inner circle
        painter.drawEllipse(
            cx - radius * scale['center_ring'],
            cy - radius * scale['center_ring'],
            radius * scale['center_ring'] * 2,
            radius * scale['center_ring'] * 2
        )
        
        # Draw zodiac elements
        self.draw_zodiac_symbols(painter, cx, cy, radius)
        
        # Draw house lines and cusps
        self.draw_house_lines(painter, cx, cy, radius)
        if hasattr(self, 'houses') and self.houses:
            self.draw_house_cusps(painter, cx, cy, radius)
        
        # Draw nakshatra elements
        self.draw_nakshatra_lines(painter, cx, cy, radius)
        self.draw_nakshatras(painter, cx, cy, radius)

    def toggle_transits(self):
        """Toggle transit display and update the chart"""
        print("\nDEBUG - toggle_transits called")
        self.show_transits = self.transit_action.isChecked()
        print(f"Show transits set to: {self.show_transits}")
        
        # If toggling on and no transit data exists, calculate current positions
        if self.show_transits and not self.transit_data:
            print("No transit data available - need to calculate current positions")
            # You'll need to implement this part to get current planetary positions
            self.calculate_current_transits()
        else:
            print(f"Transit data exists: {self.transit_data is not None}")
        
        self.update()  # Force redraw
        print("Chart update requested")

    def calculate_current_transits(self):
        """Calculate current planetary positions for transits"""
        try:
            from datetime import datetime
            current_time = datetime.now()
            
            # Create transit data structure without Ascendant
            self.transit_data = {
                'Sun': {'longitude': 0, 'sign': 'Aries', 'degree': 0},
                'Moon': {'longitude': 30, 'sign': 'Taurus', 'degree': 0},
                'Mercury': {'longitude': 60, 'sign': 'Gemini', 'degree': 0},
                'Venus': {'longitude': 90, 'sign': 'Cancer', 'degree': 0},
                'Mars': {'longitude': 120, 'sign': 'Leo', 'degree': 0},
                'Jupiter': {'longitude': 150, 'sign': 'Virgo', 'degree': 0},
                'Saturn': {'longitude': 180, 'sign': 'Libra', 'degree': 0},
                # Note: Some astrologers include Rahu/Ketu in transits, others don't
                'Rahu': {'longitude': 210, 'sign': 'Scorpio', 'degree': 0},
                'Ketu': {'longitude': 30, 'sign': 'Taurus', 'degree': 0}
            }
            
            # Add is_retrograde flag for all planets
            for planet_data in self.transit_data.values():
                planet_data['is_retrograde'] = False
            
            print(f"Calculated transit data: {self.transit_data}")
        except Exception as e:
            print(f"Error calculating transits: {str(e)}")
            traceback.print_exc()

    def update_transit_data(self, transit_data):
        """Update transit planetary positions"""
        print(f"\nDEBUG - Updating transit data: {transit_data}")
        self.transit_data = transit_data
        if self.show_transits:
            self.update()  # Only redraw if transits are visible

    def group_planets_by_proximity(self, points, proximity_threshold):
        """
        Group planets that are within proximity_threshold degrees of each other.
        Returns a list of groups, where each group is a list of planet names.
        """
        groups = []
        used_planets = set()
        
        for planet1 in points:
            if planet1 in used_planets:
                continue
            
            current_group = [planet1]
            used_planets.add(planet1)
            
            for planet2 in points:
                if planet2 in used_planets:
                    continue
                
                lon1 = points[planet1]['longitude']
                lon2 = points[planet2]['longitude']
                
                # Calculate angular distance
                diff = abs(lon1 - lon2)
                if diff > 180:
                    diff = 360 - diff
                    
                if diff <= proximity_threshold:
                    current_group.append(planet2)
                    used_planets.add(planet2)
                
            groups.append(current_group)
        
        return groups

    def toggle_considerations(self):
        """Toggle display of horary considerations"""
        is_checked = self.consideration_action.isChecked()
        print(f"Toggling considerations display: {is_checked}")
        # Add your consideration display logic here
        self.update()

    def toggle_dignities(self):
        """Toggle display of essential dignities"""
        is_checked = self.dignity_action.isChecked()
        print(f"Toggling dignity display: {is_checked}")
        # Add your dignity display logic here
        self.update()

    def apply_traditional_rules(self):
        """Apply traditional horary rules"""
        print("Applying traditional horary rules")
        # Add traditional rule implementation here
        pass

    def apply_modern_adaptation(self):
        """Apply modern adaptation of horary rules"""
        print("Applying modern adaptation of horary rules")
        # Add modern adaptation implementation here
        pass

    def apply_simplified_rules(self):
        """Apply simplified horary rules"""
        print("Applying simplified horary rules")
        # Add simplified rules implementation here
        pass

    def apply_advanced_analysis(self):
        """Apply advanced horary analysis"""
        print("Applying advanced horary analysis")
        # Add advanced analysis implementation here
        pass

    def resizeEvent(self, event):
        """Handle widget resize events"""
        super().resizeEvent(event)
        # Update position of Yogeswarananda container when widget is resized
        if hasattr(self, 'yogeswarananda_container'):
            self.yogeswarananda_container.move(10, self.height() - 610)

    def toggle_yogeswarananda(self, checked):
        """Toggle Yogeswarananda display"""
        if checked:
            if self.chart_data and 'yogeswarananda_12' in self.chart_data:
                yogeswarananda_data = self.chart_data['yogeswarananda_12']
                text = "Yogeswarananda 12 System:\n"
                text += "------------------------\n"
                for k, v in yogeswarananda_data.items():
                    text += f"{k}: {v}\n"
                self.yogeswarananda_display.setText(text)
                self.yogeswarananda_container.show()
            else:
                self.yogeswarananda_display.setText("No Yogeswarananda data available")
                self.yogeswarananda_container.show()
        else:
            self.yogeswarananda_container.hide()

    def show_yogeswarananda(self):
        try:
            self.house_points = {i: 0 for i in range(1, 13)}
            output = self.calculate_yogeswarananda()
            self.yogeswarananda_display.setHtml(output)
            self.yogeswarananda_container.show()
        except Exception as e:
            print(f"Error: {str(e)}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def get_house_lord(self, sign):
        """Get the lord of a sign"""
        sign_lords = {
            'Aries': 'Mars',
            'Taurus': 'Venus',
            'Gemini': 'Mercury',
            'Cancer': 'Moon',
            'Leo': 'Sun',
            'Virgo': 'Mercury',
            'Libra': 'Venus',
            'Scorpio': 'Mars',
            'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn',
            'Aquarius': 'Saturn',
            'Pisces': 'Jupiter'
        }
        return sign_lords.get(sign)

    def get_houses_owned_by(self, planet):
        """Get list of houses owned by a planet"""
        owned_houses = []
        for house_num in range(1, 13):
            house_key = f"House_{house_num}"
            house_sign = self.chart_data['houses'][house_key]['sign']
            if self.get_house_lord(house_sign) == planet:
                owned_houses.append(house_num)
        return owned_houses

    def add_points(self, house_num, points, reason=""):
        """Add points to a house and track the reason"""
        self.house_points[house_num] += points
        return f"House {house_num}: +{points} points ({reason})\n"

    def handle_rahu_ketu(self, planet, house_num, points, point_type):
        """Special handling for Rahu/Ketu points"""
        details = ""
        if planet in ['Rahu', 'Ketu']:
            house_sign = self.chart_data['houses'][f"House_{house_num}"]['sign']
            house_lord = self.get_house_lord(house_sign)
            
            # Give points to houses owned by the house lord
            for owned_house in self.get_houses_owned_by(house_lord):
                details += self.add_points(owned_house, points, 
                    f"{point_type} points via {planet}'s house lord {house_lord}")
            
            # Extra point for house lord's placement
            lord_house = None
            for h in range(1, 13):
                if self.chart_data['points'][house_lord]['house'] == h:
                    lord_house = h
                    break
            if lord_house:
                details += self.add_points(lord_house, 1, 
                    f"Extra point for {house_lord}'s placement (as {planet}'s house lord)")
        
        return details

    def calculate_house_strengths(self, x, y, z):
        """Calculate house strengths for given X, Y, Z planets"""
        output = "Point Distribution Details:\n"
        output += "-------------------------\n"
        
        # Handle X (Main Planet)
        x_data = self.chart_data['points'][x]
        if x in ['Rahu', 'Ketu']:
            output += self.handle_rahu_ketu(x, x_data['house'], 1, "Power 1: Main Planet")
        else:
            # Power 1: Houses owned by X
            for house in self.get_houses_owned_by(x):
                output += self.add_points(house, 1, f"Power 1: House owned by {x}")
        # Power 2: House where X is placed
        output += self.add_points(x_data['house'], 2, f"Power 2: House where {x} is placed")
        
        # Handle Y (Star Lord) - only if different from X
        if y != x:
            y_data = self.chart_data['points'][y]
            if y in ['Rahu', 'Ketu']:
                output += self.handle_rahu_ketu(y, y_data['house'], 3, "Power 3: Star Lord")
            else:
                # Power 3: Houses owned by Y
                for house in self.get_houses_owned_by(y):
                    output += self.add_points(house, 3, f"Power 3: House owned by {y}")
            # Power 4: House where Y is placed
            output += self.add_points(y_data['house'], 4, f"Power 4: House where {y} is placed")
        
        # Handle Z (Sub Lord)
        z_data = self.chart_data['points'][z]
        if z in ['Rahu', 'Ketu']:
            output += self.handle_rahu_ketu(z, z_data['house'], 5, "Power 5: Sub Lord")
        else:
            # Power 5: Houses owned by Z
            for house in self.get_houses_owned_by(z):
                output += self.add_points(house, 5, f"Power 5: House owned by {z}")
        # Power 6: House where Z is placed
        output += self.add_points(z_data['house'], 6, f"Power 6: House where {z} is placed")
        
        # Handle cuspal points
        for house_num in range(1, 13):
            house_data = self.chart_data['houses'][f"House_{house_num}"]
            
            # Powers 7 & 10: X as cuspal lord
            if house_data['star_lord'] == x:
                output += self.add_points(house_num, 7, f"Power 7: House where {x} is star lord of cusp")
            if house_data['sub_lord'] == x:
                output += self.add_points(house_num, 10, f"Power 10: House where {x} is sub lord of cusp")
            
            # Powers 8 & 11: Y as cuspal lord (only if different from X)
            if y != x:
                if house_data['star_lord'] == y:
                    output += self.add_points(house_num, 8, f"Power 8: House where {y} is star lord of cusp")
                if house_data['sub_lord'] == y:
                    output += self.add_points(house_num, 11, f"Power 11: House where {y} is sub lord of cusp")
            
            # Powers 9 & 12: Z as cuspal lord
            if house_data['star_lord'] == z:
                output += self.add_points(house_num, 9, f"Power 9: House where {z} is star lord of cusp")
            if house_data['sub_lord'] == z:
                output += self.add_points(house_num, 12, f"Power 12: House where {z} is sub lord of cusp")
        
        return output

    def calculate_single_planet(self, planet, role):
        """Helper method to calculate for a single planet"""
        x_data = self.chart_data['points'][planet]
        y = x_data['star_lord']
        z = x_data['sub_lord']
        
        details = f"Planets Involved:\n"
        details += f"{role} (X): {planet}\n"
        details += f"Star Lord (Y): {y}\n"
        details += f"Sub Lord (Z): {z}\n\n"
        
        details += self.calculate_house_strengths(planet, y, z)
        details += "\nResults:\n"
        for house, points in self.house_points.items():
            details += f"House {house}: {points} points\n"
        
        return details

    def calculate_yogeswarananda(self):
        try:
            output = "<pre>"  # Use pre-formatted text
            output += "Yogeswarananda Summary\n"
            output += "====================\n\n"
            
            # Dictionary to store all results
            all_results = {}
            
            # 1. Moon calculation
            moon_data = self.chart_data['points']['Moon']
            moon_star_lord = moon_data['star_lord']
            moon_sub_lord = moon_data['sub_lord']
            
            self.house_points = {i: 0 for i in range(1, 13)}
            self.calculate_single_planet('Moon', "X")
            all_results['Moon'] = {
                'combination': f"Moon-{moon_star_lord}-{moon_sub_lord}",
                'points': self.house_points.copy()
            }

            # 2. Moon's star lord
            star_lord_data = self.chart_data['points'][moon_star_lord]
            star_lord_star = star_lord_data['star_lord']
            star_lord_sub = star_lord_data['sub_lord']
            
            self.house_points = {i: 0 for i in range(1, 13)}
            self.calculate_single_planet(moon_star_lord, "X")
            all_results[moon_star_lord] = {
                'combination': f"{moon_star_lord}-{star_lord_star}-{star_lord_sub}",
                'points': self.house_points.copy()
            }

            # Calculate remaining planets
            remaining_planets = [p for p in ['Sun', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'] 
                               if p != moon_star_lord]

            for planet in remaining_planets:
                planet_data = self.chart_data['points'][planet]
                self.house_points = {i: 0 for i in range(1, 13)}
                self.calculate_single_planet(planet, "X")
                all_results[planet] = {
                    'combination': f"{planet}-{planet_data['star_lord']}-{planet_data['sub_lord']}",
                    'points': self.house_points.copy()
                }

            # Format output with explicit line breaks
            count = 1
            for planet, result in all_results.items():
                output += f"{count}. {result['combination']}\n"
                self.house_points = result['points']
                output += "   " + self.format_house_points() + "\n\n"
                count += 1

            output += "</pre>"  # Close pre-formatted text
            return output
            
        except Exception as e:
            import traceback
            return f"Error in calculations: {str(e)}\n{traceback.format_exc()}"

    def format_house_points(self):
        """Format house points with larger superscript notation"""
        points_list = []
        for house in range(1, 13):
            points = self.house_points[house]
            # Made the superscript size larger (20px)
            points_list.append(f"{house}<sup style='font-size: 20px'>{points}</sup>")
        
        return ", ".join(points_list)

class PlanetIconManager:
    def __init__(self):
        self.icons = {}
        self.load_icons()
    
    def load_icons(self):
        icon_path = "path/to/icons/"
        self.icons = {
            'Sun': QtGui.QIcon(f"{icon_path}sun.svg"),
            'Moon': QtGui.QIcon(f"{icon_path}moon.svg"),
            'Mercury': QtGui.QIcon(f"{icon_path}mercury.svg"),
            # ... etc for other planets
        }
    
    def draw_planet_icon(self, painter, planet, x, y, size):
        if planet in self.icons:
            self.icons[planet].paint(painter, QtCore.QRect(x-size//2, y-size//2, size, size))

class PlanetSymbolDrawer:
    @staticmethod
    def draw_sun(painter, x, y, size):
        # Draw circle with rays
        painter.drawEllipse(x-size//4, y-size//4, size//2, size//2)
        # Draw rays
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = x + (size//3) * math.cos(rad)
            y1 = y + (size//3) * math.sin(rad)
            x2 = x + (size//2) * math.cos(rad)
            y2 = y + (size//2) * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    @staticmethod
    def draw_moon(painter, x, y, size):
        # Draw crescent
        path = QtGui.QPainterPath()
        path.arcTo(x-size//2, y-size//2, size, size, 30, 300)
        painter.drawPath(path)

class EnhancedPlanetDisplay:
    # Define class constants
    PLANET_SYMBOLS = {
        'Sun': '☉', 
        'Moon': '☽', 
        'Mercury': '☿', 
        'Venus': '♀', 
        'Mars': '♂',
        'Jupiter': '♃', 
        'Saturn': '♄', 
        'Uranus': '♅',    # Added
        'Neptune': '♆',    # Added
        'Pluto': '♇',     # Added
        'Rahu': '☊', 
        'Ketu': '☋',
        'Ascendant': 'Asc'
    }
    
    PLANET_COLORS = {
        'Sun': QtGui.QColor(255, 140, 0),      # Orange
        'Moon': QtGui.QColor(192, 192, 192),    # Silver
        'Mars': QtGui.QColor(255, 0, 0),        # Red
        'Mercury': QtGui.QColor(0, 255, 0),     # Green
        'Jupiter': QtGui.QColor(255, 255, 0),   # Yellow
        'Venus': QtGui.QColor(0, 255, 255),     # Cyan
        'Saturn': QtGui.QColor(128, 128, 128),  # Gray
        'Rahu': QtGui.QColor(0, 0, 128),        # Navy
        'Ketu': QtGui.QColor(128, 0, 0),        # Maroon
        'Ascendant': QtGui.QColor(255, 255, 255) # White
    }

    def __init__(self, style='basic', points=None):
        self._style = style  # Changed to private attribute
        self._points = points
        print(f"Creating new EnhancedPlanetDisplay with style: {style}")
    
    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, value):
        self._style = value
        
    @property
    def points(self):
        return self._points
    
    @points.setter
    def points(self, value):
        self._points = value

    def draw_planet(self, painter, planet, x, y, size):
        painter.save()
        planet_color = self.PLANET_COLORS.get(planet, QtGui.QColor(255, 255, 255))
        
        if self.style == 'text':
            # Get center of chart for angle calculation
            center_x = painter.device().width() / 2
            center_y = painter.device().height() / 2
            dx = x - center_x
            dy = y - center_y
            angle = math.degrees(math.atan2(dy, dx))
            
            # Format text with degree in brackets
            if planet == 'Ascendant':
                name_text = "Asc"
            else:
                name_text = planet
                
            # Add degree information for text style
            if self.points and planet in self.points:
                degree = self.points[planet].get('degree', 0)
                display_text = f"{name_text} ({degree:.1f}°)"
            else:
                display_text = name_text
            
            # Position and rotate text
            painter.translate(x, y)
            painter.rotate(angle)
            if angle > 90 or angle < -90:
                painter.rotate(180)
            
            # Set font and color for text style
            font = QtGui.QFont('Arial', int(size/2))
            painter.setFont(font)
            painter.setPen(QPen(planet_color, 1))
            
            # Draw the combined text
            text_rect = QtCore.QRect(
                -int(size * 3),
                -int(size/2),
                int(size * 6),  # Added missing closing parenthesis
                int(size)
            )  # Ensure this closing parenthesis is present
            alignment = Qt.AlignmentFlag.AlignLeft if (-90 <= angle <= 90) else Qt.AlignmentFlag.AlignRight
            painter.drawText(text_rect, alignment, display_text)
            
        else:
            # All other styles (basic, geometric, enhanced, labeled) remain unchanged
            if self.style == 'basic':
                # Basic symbol only
                painter.setPen(QPen(planet_color, 2))
                font = QtGui.QFont('Arial', size)
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
            elif self.style == 'geometric':
                # Geometric style remains unchanged
                painter.setBrush(QtGui.QBrush(planet_color.lighter(150)))
                painter.setPen(QPen(planet_color, 2))
                painter.drawEllipse(x-size//2, y-size//2, size, size)
                
                painter.setPen(QPen(planet_color.darker(150), 2))
                font = QtGui.QFont('Arial', int(size * 0.8))
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
            elif self.style == 'enhanced':
                # Draw glow effect
                glow = QtWidgets.QGraphicsDropShadowEffect()
                glow.setColor(planet_color)
                glow.setBlurRadius(size//4)
                
                # Draw circular background
                painter.setBrush(QtGui.QBrush(planet_color.lighter(170)))
                painter.setPen(QPen(planet_color, 2))
                painter.drawEllipse(x-size//2, y-size//2, size, size)
                
                # Draw symbol
                painter.setPen(QPen(planet_color.darker(150), 2))
                font = QtGui.QFont('Arial', int(size * 0.8))
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2, size, size,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
            elif self.style == 'labeled':
                # Draw background circle
                painter.setBrush(QtGui.QBrush(planet_color.lighter(170)))
                painter.setPen(QPen(planet_color, 2))
                painter.drawEllipse(x-size//2, y-size//2, size, size)
                
                # Draw symbol
                painter.setPen(QPen(planet_color.darker(150), 2))
                font = QtGui.QFont('Arial', int(size * 0.6))
                painter.setFont(font)
                painter.drawText(x-size//2, y-size//2-5, size, size//2,
                               Qt.AlignmentFlag.AlignCenter,
                               self.PLANET_SYMBOLS[planet])
                
                # Draw planet name below
                font.setPointSize(int(size * 0.3))
                painter.setFont(font)
                painter.drawText(x-size//2, y, size, size//2,
                               Qt.AlignmentFlag.AlignCenter,
                               planet[:3])  # First 3 letters of planet name
        
        painter.restore()

class StylePreviewDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        
        # Get style name
        style_name = index.data()
        
        # Draw style name
        text_rect = option.rect.adjusted(50, 0, 0, 0)  # Make room for preview
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, style_name)
        
        # Draw preview
        preview_rect = QRect(option.rect.left() + 5, option.rect.top() + 5,
                           40, option.rect.height() - 10)
        
        # Create temporary planet display to draw preview
        planet_display = EnhancedPlanetDisplay(style=style_name)
        planet_display.draw_planet(painter, 'Sun', 
                                 preview_rect.center().x(),
                                 preview_rect.center().y(),
                                 min(preview_rect.width(), preview_rect.height()))

    def sizeHint(self, option, index):
        return QSize(200, 40)  # Make items tall enough for preview

class CustomTooltip(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Create label with explicit large font
        self.label = QLabel()
        font = QFont('Arial', 48)  # Extremely large font size
        font.setBold(True)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        # Set fixed large size
        self.setMinimumWidth(800)
        self.setMinimumHeight(300)
        
        # Basic styling
        self.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border: 6px solid #404040;
                border-radius: 20px;
            }
            QLabel {
                color: white;
                padding: 20px;
            }
        """)
        
        # Timer for auto-hide
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)
        
        self.hide()

    def show_tooltip(self, text, global_pos):
        """Show tooltip with text at given position"""
        # Format text
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if ':' in line:
                label, value = line.split(':', 1)
                formatted_lines.append(f"{label}:{value}")
            else:
                formatted_lines.append(line)
                
        formatted_text = '\n'.join(formatted_lines)
        
        self.label.setText(formatted_text)
        
        # Position tooltip
        screen = QApplication.screenAt(global_pos)
        if screen:
            screen_geometry = screen.geometry()
            x = global_pos.x() + 40
            y = global_pos.y() + 40
            
            # Adjust if would go off screen
            if x + self.width() > screen_geometry.right():  # Assuming tooltip width of 350px
                x = global_pos.x() - self.width() - 40
            if y + self.height() > screen_geometry.bottom():  # Assuming tooltip height of 200px
                y = global_pos.y() - self.height() - 40
            
            self.move(x, y)
        
        self.show()
        self.hide_timer.start(3000)

    def hideEvent(self, event):
        self.hide_timer.stop()
        super().hideEvent(event)

    def set_theme(self, theme):
        """Update tooltip styling based on theme"""
        if theme == 'Dark':
            self.setStyleSheet("""
                QFrame {
                    background-color: #2D2D2D;
                    border: 6px solid #404040;
                    border-radius: 20px;
                }
                QLabel {
                    color: white;
                    padding: 20px;
                }
            """)
        else:  # Light theme
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F5;
                    border: 6px solid #D3D3D3;
                    border-radius: 20px;
                }
                QLabel {
                    color: black;
                    padding: 20px;
                }
            """)

def mouseMoveEvent(self, event):
    """Handle mouse movement for tooltips"""
    try:
        # Create tooltip if it doesn't exist
        if not hasattr(self, 'custom_tooltip'):
            self.custom_tooltip = CustomTooltip(self)
        
        # Get chart dimensions
        width = self.width()
        height = self.height()
        cx = width // 2
        cy = height // 2
        radius = min(width, height) // 2 - 40
        
        # Calculate mouse position relative to center
        dx = event.pos().x() - cx
        dy = event.pos().y() - cy
        current_radius = math.sqrt(dx*dx + dy*dy)
        
        # Calculate angle
        angle = math.degrees(math.atan2(-dy, dx))
        if angle < 0:
            angle += 360
        chart_angle = (270 - angle) % 360
        
        # Define ring boundaries
        outer_radius = radius
        middle_radius = radius * 0.85
        inner_radius = radius * 0.7
        
        # Check which ring the mouse is in
        if middle_radius < current_radius < outer_radius:
            # Nakshatra ring
            nakshatra_index = int((chart_angle / (360/27))) % 27
            nakshatra_list = list(self.nakshatra_info.keys())
            if nakshatra_index < len(nakshatra_list):
                nakshatra_name = nakshatra_list[nakshatra_index]
                tooltip_text = self.nakshatra_info[nakshatra_name]
                self.custom_tooltip.show_tooltip(tooltip_text, event.globalPos())
                
        elif inner_radius < current_radius < middle_radius:
            # Zodiac ring
            sign_index = int((chart_angle / 30)) % 12
            signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
            if sign_index < len(signs):
                sign_name = signs[sign_index]
                tooltip_text = f"Sign: {sign_name}\nDegree: {chart_angle % 30:.1f}°"
                self.custom_tooltip.show_tooltip(tooltip_text, event.globalPos())
                
        elif current_radius < inner_radius:
            # Planet ring - check for planets near mouse position
            found_planet = False
            for planet, data in self.points.items():
                planet_angle = (90 - float(data['longitude'])) % 360
                angle_diff = abs(chart_angle - planet_angle)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                    
                if angle_diff < 5:  # Within 5 degrees
                    found_planet = True
                    tooltip_text = (f"Planet: {planet}\n"
                                  f"Sign: {data['sign']}\n"
                                  f"Degree: {data['degree']:.1f}°\n"
                                  f"House: {data.get('house', 'N/A')}")
                    if 'nakshatra' in data:
                        tooltip_text += f"\nNakshatra: {data['nakshatra']}"
                    if 'pada' in data:
                        tooltip_text += f"\nPada: {data['pada']}"
                    self.custom_tooltip.show_tooltip(tooltip_text, event.globalPos())
                    break
            
            if not found_planet:
                self.custom_tooltip.hide()
        else:
            self.custom_tooltip.hide()
            
    except Exception as e:
        print(f"Error in mouseMoveEvent: {str(e)}")
        import traceback
        traceback.print_exc()
