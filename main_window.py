import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cosmic Calculator")
        self.setGeometry(100, 100, 800, 600)
        
        # Create web view widget
        self.web_view = QWebEngineView(self)
        self.web_view.setUrl(QUrl("http://localhost:5000"))
        self.setCentralWidget(self.web_view)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 