import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from .gui.main_window import MainWindow

def main():
    # Set AppUserModelID for Windows taskbar icon
    if os.name == 'nt':
        myappid = 'rupeshknn.sem_view.viewer.1.0' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), 'gui', 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    window = MainWindow()
    window.show()
    
    # Check for command line arguments (file to open)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        # Verify it's a file
        if os.path.isfile(file_path):
            window.load_image(file_path)
            
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
