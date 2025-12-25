from PySide6.QtWidgets import QMainWindow, QFileDialog, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QStatusBar
from PySide6.QtGui import QAction, QPixmap, QImage
from PySide6.QtCore import Qt
import tifffile
import numpy as np
from gui.canvas import ImageCanvas
from utils.metadata_parser import get_pixel_scale

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEM Image Viewer")
        self.resize(1000, 800)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Canvas
        self.canvas = ImageCanvas()
        layout.addWidget(self.canvas)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.scale_label = QLabel("Scale: N/A")
        self.status_bar.addPermanentWidget(self.scale_label)
        
        # Instructions
        self.status_bar.showMessage("Right-click & drag to measure. Left-click & drag to pan. Wheel to zoom.")

        # Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SEM Image", "", "TIFF Files (*.tif *.tiff);;All Files (*)")
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        try:
            # Load image data
            with tifffile.TiffFile(file_path) as tif:
                image_data = tif.asarray()
                
                # Handle metadata
                pixel_scale = get_pixel_scale(file_path)
                self.canvas.set_scale(pixel_scale)
                if pixel_scale:
                    self.scale_label.setText(f"Scale: {pixel_scale * 1e9:.2f} nm/px")
                else:
                    self.scale_label.setText("Scale: Unknown")

            # Normalize and convert to QImage
            if image_data.ndim == 2:
                height, width = image_data.shape
                
                # Normalize to 8-bit
                if image_data.dtype != np.uint8:
                    image_data = image_data.astype(np.float32)
                    image_data = (image_data - image_data.min()) / (image_data.max() - image_data.min()) * 255
                    image_data = image_data.astype(np.uint8)
                
                bytes_per_line = width
                q_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
                pixmap = QPixmap.fromImage(q_image)
                
                self.canvas.set_image(pixmap)
                self.status_bar.showMessage(f"Loaded: {file_path}. Right-click to measure.")
            else:
                self.status_bar.showMessage("Error: Only 2D images supported.")

        except Exception as e:
            self.status_bar.showMessage(f"Error loading file: {str(e)}")
            print(f"Error: {e}")
