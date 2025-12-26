from PySide6.QtWidgets import QMainWindow, QFileDialog, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QStatusBar, QToolBar, QDockWidget, QTextEdit, QMessageBox
from PySide6.QtGui import QAction, QPixmap, QImage, QPainter, QColor
from PySide6.QtCore import Qt
import tifffile
import numpy as np
import os
import shutil
from gui.canvas import ImageCanvas
from utils.metadata_parser import get_pixel_scale, get_metadata_context

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEM Image Viewer")
        self.resize(1200, 800)

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

        # Toolbar
        self.toolbar = QToolBar("Tools")
        self.addToolBar(self.toolbar)
        
        self.measure_action = QAction("📏 Measure", self)
        self.measure_action.setCheckable(True)
        self.measure_action.setChecked(True)
        self.measure_action.triggered.connect(lambda: self.set_mode(ImageCanvas.MODE_MEASURE))
        self.toolbar.addAction(self.measure_action)
        
        self.polygon_action = QAction("⬠ Area", self)
        self.polygon_action.setCheckable(True)
        self.polygon_action.triggered.connect(lambda: self.set_mode(ImageCanvas.MODE_POLYGON))
        self.toolbar.addAction(self.polygon_action)
        
        self.clear_action = QAction("🗑 Clear", self)
        self.clear_action.triggered.connect(self.canvas.clear_measurements)
        self.toolbar.addAction(self.clear_action)

        # Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Annotated", self)
        save_action.triggered.connect(self.save_annotated)
        file_menu.addAction(save_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Metadata Dock
        self.metadata_dock = QDockWidget("Image Context", self)
        self.metadata_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_dock.setWidget(self.metadata_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.metadata_dock)
        
        self.current_file_path = None
        self.original_image_data = None

    def set_mode(self, mode):
        self.canvas.set_mode(mode)
        if mode == ImageCanvas.MODE_MEASURE:
            self.measure_action.setChecked(True)
            self.polygon_action.setChecked(False)
            self.status_bar.showMessage("Mode: Measure - Right-click start point, Right-click end point. Left-click & drag to pan.")
        else:
            self.measure_action.setChecked(False)
            self.polygon_action.setChecked(True)
            self.status_bar.showMessage("Mode: Area - Right-click to add vertices. Double-click to finish. Left-click & drag to pan.")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SEM Image", "", "TIFF Files (*.tif *.tiff);;All Files (*)")
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        try:
            self.current_file_path = file_path
            # Load image data
            with tifffile.TiffFile(file_path) as tif:
                self.original_image_data = tif.asarray()
                
                # Handle metadata
                pixel_scale = get_pixel_scale(file_path)
                self.canvas.set_scale(pixel_scale)
                if pixel_scale:
                    self.scale_label.setText(f"Scale: {pixel_scale * 1e9:.2f} nm/px")
                else:
                    self.scale_label.setText("Scale: Unknown")
                    
                # Context
                context = get_metadata_context(file_path)
                self.display_context(context)

            # Normalize and convert to QImage
            image_data = self.original_image_data
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
                self.status_bar.showMessage(f"Loaded: {file_path}")
            else:
                self.status_bar.showMessage("Error: Only 2D images supported.")

        except Exception as e:
            self.status_bar.showMessage(f"Error loading file: {str(e)}")
            print(f"Error: {e}")

    def display_context(self, context):
        text = "<h2>Image Details</h2>"
        if context:
            text += "<ul>"
            for k, v in context.items():
                text += f"<li><b>{k}:</b> {v}</li>"
            text += "</ul>"
        else:
            text += "<p>No context metadata found.</p>"
        self.metadata_text.setHtml(text)

    def save_annotated(self):
        if not self.current_file_path or self.original_image_data is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Annotated Image", "", "TIFF Files (*.tif)")
        if not file_path:
            return
            
        try:
            # Create a QImage from the original data to render annotations on
            # Convert grayscale to RGB
            if self.original_image_data.dtype == np.uint8:
                gray_data = self.original_image_data
            else:
                # Normalize if not uint8
                d = self.original_image_data.astype(np.float32)
                gray_data = ((d - d.min()) / (d.max() - d.min()) * 255).astype(np.uint8)
                
            height, width = gray_data.shape
            # Create RGB image (Format_RGB888)
            # We need to construct it from the grayscale data
            # QImage(data, w, h, fmt) needs data to be kept alive
            # Let's convert to RGB numpy array first
            rgb_data = np.stack((gray_data,)*3, axis=-1)
            q_img = QImage(rgb_data.data, width, height, width*3, QImage.Format_RGB888)
            
            # Create a painter to draw annotations on this image
            # We need to make a copy to draw on, or QPainter might fail on read-only buffer
            annotated_q_img = q_img.copy()
            
            painter = QPainter(annotated_q_img)
            # We need to align the scene rect with the image
            # The scene might be larger or offset?
            # The pixmap item is at (0,0) usually.
            # Let's render the scene.
            self.canvas.scene.render(painter)
            painter.end()
            
            # Convert back to numpy
            ptr = annotated_q_img.constBits()
            stride = annotated_q_img.bytesPerLine()
            arr = np.array(ptr).reshape(height, stride)
            arr = arr[:, :width * 3] # RGB is 3 bytes/pixel
            annotated_rgb = arr.reshape(height, width, 3)
            
            # Save as Multi-page TIFF
            # Page 0: Annotated RGB (for viewing)
            # Page 1: Original Grayscale (for data)
            with tifffile.TiffWriter(file_path) as tif:
                tif.write(annotated_rgb, photometric='rgb', description="Annotated Image")
                tif.write(self.original_image_data, photometric='minisblack', description="Original Raw Data")
                
            self.status_bar.showMessage(f"Saved: Page 0 (Annotated), Page 1 (Raw) to {file_path}")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error saving: {str(e)}")

    def closeEvent(self, event):
        # Clean up temp_data directory
        temp_dir = os.path.join(os.getcwd(), "temp_data")
        if os.path.exists(temp_dir):
            try:
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")
            except Exception as e:
                print(f"Error cleaning temp_data: {e}")
        
        event.accept()

