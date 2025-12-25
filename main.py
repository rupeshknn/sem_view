import sys
import os
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
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
