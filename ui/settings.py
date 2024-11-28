from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QRadioButton, 
    QComboBox, QLabel
)

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Zodiac System
        self.zodiac_group = QGroupBox("Zodiac System")
        zodiac_layout = QVBoxLayout()
        self.sidereal_radio = QRadioButton("Sidereal")
        self.tropical_radio = QRadioButton("Tropical")
        self.tropical_radio.setChecked(True)
        zodiac_layout.addWidget(self.sidereal_radio)
        zodiac_layout.addWidget(self.tropical_radio)
        self.zodiac_group.setLayout(zodiac_layout)
        layout.addWidget(self.zodiac_group)

        # Add other settings (house system, ayanamsa, etc.)
        self.add_combo_setting(layout, "House System", 
                             ["Placidus", "Equal", "Whole Sign", "Topocentric"])
        self.add_combo_setting(layout, "Ayanamsa", 
                             ["Lahiri", "Raman", "Krishnamurti"])
        # ... add other settings ...

    def add_combo_setting(self, layout, label_text, items):
        layout.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItems(items)
        layout.addWidget(combo)
        setattr(self, f"{label_text.lower().replace(' ', '_')}_combo", combo) 