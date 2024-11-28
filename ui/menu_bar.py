from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenuBar

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_menus()

    def init_menus(self):
        # File Menu
        file_menu = self.addMenu('File')
        
        new_action = QAction('New Chart', self)
        new_action.triggered.connect(self.parent.new_chart)
        
        open_action = QAction('Open Chart', self)
        open_action.triggered.connect(self.parent.open_chart)
        
        save_action = QAction('Save Chart', self)
        save_action.triggered.connect(self.parent.save_chart)
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.parent.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = self.addMenu('View')
        divisional_charts_action = QAction('Divisional Charts', self)
        divisional_charts_action.triggered.connect(self.parent.show_divisional_charts)
        view_menu.addAction(divisional_charts_action)

        # Help Menu
        help_menu = self.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.parent.show_about)
        help_action = QAction('Help', self)
        help_action.triggered.connect(self.parent.show_help)
        help_menu.addAction(about_action)
        help_menu.addAction(help_action) 