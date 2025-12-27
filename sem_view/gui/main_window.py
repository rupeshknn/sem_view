from PySide6.QtWidgets import QMainWindow, QFileDialog, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QStatusBar, QToolBar, QDockWidget, QTextEdit, QListWidget, QListWidgetItem, QStyle, QCheckBox
from PySide6.QtGui import QAction, QPixmap, QImage, QPainter, QColor
from PySide6.QtCore import Qt, QSize, QTemporaryDir, QRectF
import tifffile
import numpy as np
import os
import shutil
import json
from .canvas import ImageCanvas
from ..utils.metadata_parser import get_pixel_scale, get_metadata_context

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
        self.status_bar.showMessage("Select a tool.  |  🖱️ Middle-drag to pan  |  🔍 Wheel to zoom")

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32)) # Larger icons
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon) # Text under icon for clarity
        self.addToolBar(self.toolbar)
        
        # File Actions
        open_action = QAction("Open File", self)
        open_action.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(open_action)

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        open_folder_action.triggered.connect(self.open_folder)
        self.toolbar.addAction(open_folder_action)
        
        save_action = QAction("Save", self)
        save_action.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        save_action.triggered.connect(self.save_annotated)
        self.toolbar.addAction(save_action)

        self.toolbar.addSeparator()

        # Tool Actions
        # Load custom icons
        ruler_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'ruler.png')
        polygon_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'polygon.png')
        
        self.measure_action = QAction("Measure", self)
        if os.path.exists(ruler_icon_path):
            self.measure_action.setIcon(QPixmap(ruler_icon_path))
        self.measure_action.setCheckable(True)
        self.measure_action.setChecked(True)
        self.measure_action.triggered.connect(lambda: self.set_mode(ImageCanvas.MODE_MEASURE))
        self.toolbar.addAction(self.measure_action)
        
        self.polygon_action = QAction("Area", self)
        if os.path.exists(polygon_icon_path):
            self.polygon_action.setIcon(QPixmap(polygon_icon_path))
        self.polygon_action.setCheckable(True)
        self.polygon_action.triggered.connect(lambda: self.set_mode(ImageCanvas.MODE_POLYGON))
        self.toolbar.addAction(self.polygon_action)
        
        self.clear_action = QAction("Clear", self)
        self.clear_action.setIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton))
        self.clear_action.triggered.connect(self.canvas.clear_measurements)
        self.toolbar.addAction(self.clear_action)
        
        self.toolbar.addSeparator()
        
        # Save Options
        # Save Options
        self.burn_in_checkbox = QCheckBox("Burn-in Annotations", self)
        self.burn_in_checkbox.setChecked(False) # Default to Active Elements
        self.burn_in_checkbox.setToolTip("Checked: Annotations are permanently burned into the image pixels (Not editable).\nUnchecked: Annotations are saved as editable vectors (Active Elements).")
        self.toolbar.addWidget(self.burn_in_checkbox)
        
        self.toolbar.addSeparator()
        
        self.toolbar.addSeparator()
        
        self.toolbar.addSeparator()
        
        # Page Navigation
        self.prev_page_action = QAction("◀", self)
        self.prev_page_action.triggered.connect(self.prev_page)
        self.prev_page_action.setEnabled(False)
        self.toolbar.addAction(self.prev_page_action)
        
        self.page_label = QLabel(" Page 1/1 ")
        self.toolbar.addWidget(self.page_label)
        
        self.next_page_action = QAction("▶", self)
        self.next_page_action.triggered.connect(self.next_page)
        self.next_page_action.setEnabled(False)
        self.toolbar.addAction(self.next_page_action)

        self.toolbar.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        exit_action.triggered.connect(self.close)
        self.toolbar.addAction(exit_action)
        
        # Metadata Dock
        self.metadata_dock = QDockWidget("Image Context", self)
        self.metadata_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        
        self.metadata_widget = QWidget()
        self.metadata_layout = QVBoxLayout(self.metadata_widget)
        self.metadata_layout.setContentsMargins(0, 0, 0, 0)
        
        # Show Annotations Toggle
        self.show_annotations_checkbox = QCheckBox("Show Annotations")
        self.show_annotations_checkbox.setChecked(True)
        self.show_annotations_checkbox.toggled.connect(self.toggle_annotations_visibility)
        self.metadata_layout.addWidget(self.show_annotations_checkbox)
        
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_layout.addWidget(self.metadata_text)
        
        self.metadata_dock.setWidget(self.metadata_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.metadata_dock)

        # File Browser Dock
        self.file_dock = QDockWidget("File Browser", self)
        self.file_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_file_from_list)
        self.file_dock.setWidget(self.file_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)
        self.file_dock.hide() # Hide initially
        
        self.current_file_path = None
        self.original_image_data = None
        self.image_pages = []
        self.current_page_index = 0
        self.current_annotations = None
        
        # Temporary Directory (auto-cleaned)
        self.temp_dir = QTemporaryDir()
        if not self.temp_dir.isValid():
            print("Warning: Could not create temporary directory.")

    def set_mode(self, mode):
        self.canvas.set_mode(mode)
        if mode == ImageCanvas.MODE_MEASURE:
            self.measure_action.setChecked(True)
            self.polygon_action.setChecked(False)
            self.status_bar.showMessage("📏 Click start ➜ Click end  |  🖱️ Middle-drag to pan")
        else:
            self.measure_action.setChecked(False)
            self.polygon_action.setChecked(True)
            self.status_bar.showMessage("⬠ Click to add points  |  Right-click to finish  |  🖱️ Middle-drag to pan")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SEM Image", "", "TIFF Files (*.tif *.tiff);;All Files (*)")
        if file_path:
            self.load_image(file_path)
            # If opening a single file, we might want to hide the file browser or clear it?
            # For now, let's just leave it as is, or maybe populate it with just that file?
            # Let's keep it simple: Open File just opens the file.

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder with SEM Images")
        if folder_path:
            self.populate_file_list(folder_path)
            self.file_dock.show()

    def populate_file_list(self, folder_path):
        self.file_list.clear()
        self.current_folder = folder_path
        
        # Find TIFF files
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.tif', '.tiff'))]
        files.sort()
        
        if not files:
            self.status_bar.showMessage(f"No TIFF files found in {folder_path}")
            return

        for f in files:
            item = QListWidgetItem(f)
            self.file_list.addItem(item)
            
        self.status_bar.showMessage(f"Found {len(files)} images in {folder_path}")

    def load_file_from_list(self, item):
        if not hasattr(self, 'current_folder'):
            return
            
        file_name = item.text()
        file_path = os.path.join(self.current_folder, file_name)
        self.load_image(file_path)

    def load_image(self, file_path):
        try:
            self.current_file_path = file_path
            # Load image data
            with tifffile.TiffFile(file_path) as tif:
                # Load all pages
                self.image_pages = []
                for page in tif.pages:
                    data = page.asarray()
                    
                    # Check for palette (colormap)
                    if page.colormap is not None:
                        # Colormap is typically (3, 2**bps)
                        # We need to transpose it to (N, 3) for indexing
                        palette = np.array(page.colormap).T
                        
                        # Normalize to 8-bit if necessary (often 16-bit in TIFF)
                        if palette.max() > 255:
                            palette = (palette / 256).astype(np.uint8)
                        else:
                            palette = palette.astype(np.uint8)
                            
                        # Apply palette to indices
                        # data contains indices, we map them to RGB
                        if data.ndim == 2:
                            rgb_data = palette[data]
                            self.image_pages.append(rgb_data)
                        else:
                            # Fallback if dimensions are unexpected
                            self.image_pages.append(data)
                    else:
                        self.image_pages.append(data)

                self.current_page_index = 0
                
                # Handle metadata (from first page)
                pixel_scale = get_pixel_scale(file_path)
                self.canvas.set_scale(pixel_scale)
                if pixel_scale:
                    self.scale_label.setText(f"Scale: {pixel_scale * 1e9:.2f} nm/px")
                else:
                    self.scale_label.setText("Scale: Unknown")
                    
                # Context
                context = get_metadata_context(file_path)
                self.display_context(context)
                
                # Store annotations if present
                if 'Annotations' in context:
                    self.current_annotations = context['Annotations']
                else:
                    self.current_annotations = None
                    
                # Check if burnt-in
                is_burnt_in = context.get('is_burnt_in', False)
                if is_burnt_in:
                    self.show_annotations_checkbox.setChecked(True)
                    self.show_annotations_checkbox.setEnabled(False)
                    self.show_annotations_checkbox.setText("Show Annotations (Burnt-in)")
                    # Don't restore vectors if burnt-in to avoid duplicates
                    self.current_annotations = None 
                else:
                    self.show_annotations_checkbox.setEnabled(True)
                    self.show_annotations_checkbox.setText("Show Annotations")
                    # Restore visibility state
                    # Default to checked for now, or maybe remember last state?
                    # Let's keep it checked by default for active elements
                    self.show_annotations_checkbox.setChecked(True)

            self.update_page_controls()
            self.display_current_page()
            self.status_bar.showMessage(f"Loaded: {file_path}")

        except Exception as e:
            self.status_bar.showMessage(f"Error loading file: {str(e)}")
            print(f"Error: {e}")

    def display_current_page(self):
        if not self.image_pages:
            return
            
        image_data = self.image_pages[self.current_page_index]
        
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
        elif image_data.ndim == 3:
             # Handle RGB if loaded
             height, width, channels = image_data.shape
             if channels == 3:
                 bytes_per_line = width * 3
                 q_image = QImage(image_data.data, width, height, bytes_per_line, QImage.Format_RGB888)
                 pixmap = QPixmap.fromImage(q_image)
                 self.canvas.set_image(pixmap)
        
        # Restore annotations if we are on Page 0 and have them
        if self.current_page_index == 0 and self.current_annotations:
            self.canvas.restore_annotations_state(self.current_annotations)
        
    def update_page_controls(self):
        num_pages = len(self.image_pages)
        self.page_label.setText(f" Page {self.current_page_index + 1}/{num_pages} ")
        
        self.prev_page_action.setEnabled(num_pages > 1 and self.current_page_index > 0)
        self.next_page_action.setEnabled(num_pages > 1 and self.current_page_index < num_pages - 1)
        
    def next_page(self):
        if self.current_page_index < len(self.image_pages) - 1:
            self.current_page_index += 1
            self.display_current_page()
            self.update_page_controls()
            
    def prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.display_current_page()
            self.update_page_controls()

    def display_context(self, context):
        text = "<h2>Image Details</h2>"
        if context:
            text += "<ul>"
            for k, v in context.items():
                if k == 'Annotations':
                    continue # Skip raw annotations
                elif k == 'Measurements':
                    text += f"<li><b>{k}:</b><ul>"
                    for m in v:
                        # m is dict: type, value, unit, label, color
                        label = m.get('label', 'Unknown')
                        m_type = m.get('type', '')
                        color = m.get('color', '#000000')
                        
                        # Create a small color box
                        color_box = f"<span style='background-color:{color}; border:1px solid #000; display:inline-block; width:10px; height:10px; margin-right:5px;'>&nbsp;&nbsp;&nbsp;</span>"
                        
                        text += f"<li>{color_box} {m_type}: {label}</li>"
                    text += "</ul></li>"
                else:
                    text += f"<li><b>{k}:</b> {v}</li>"
            text += "</ul>"
        else:
            text += "<p>No context metadata found.</p>"
        self.metadata_text.setHtml(text)

    def toggle_annotations_visibility(self, visible):
        self.canvas.set_annotations_visible(visible)

    def save_annotated(self):
        if not self.current_file_path or not self.image_pages:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Annotated Image", "", "TIFF Files (*.tif)")
        if not file_path:
            return
            
        try:
            # Use the currently displayed page (or the first page?) as the base for annotation
            # Usually we annotate the main image (page 0)
            original_data = self.image_pages[0] # Assume page 0 is the one we annotate
            
            # Create a QImage from the original data to render annotations on
            # Convert grayscale to RGB
            if original_data.dtype == np.uint8:
                gray_data = original_data
            else:
                # Normalize if not uint8
                d = original_data.astype(np.float32)
                gray_data = ((d - d.min()) / (d.max() - d.min()) * 255).astype(np.uint8)
                
            height, width = gray_data.shape
            
            # Ensure contiguous array for QImage
            if not gray_data.flags['C_CONTIGUOUS']:
                gray_data = np.ascontiguousarray(gray_data)
            
            # Prepare Page 0 Data
            if self.burn_in_checkbox.isChecked():
                # Burn-in Mode: Render annotations onto image
                # Create RGB image (Format_RGB888)
                rgb_data = np.stack((gray_data,)*3, axis=-1)
                q_img = QImage(rgb_data.data, width, height, width*3, QImage.Format_RGB888)
                
                annotated_q_img = q_img.copy()
                
                painter = QPainter(annotated_q_img)
                try:
                    painter.setRenderHint(QPainter.Antialiasing)
                    painter.setRenderHint(QPainter.TextAntialiasing)
                    painter.setRenderHint(QPainter.SmoothPixmapTransform)
                    self.canvas.scene.render(painter)
                finally:
                    painter.end()
                
                # Convert back to numpy
                ptr = annotated_q_img.constBits()
                stride = annotated_q_img.bytesPerLine()
                arr = np.array(ptr).reshape(height, stride)
                arr = arr[:, :width * 3] # RGB is 3 bytes/pixel
                page0_data = arr.reshape(height, width, 3)
                
                # In Burn-in mode, we DO NOT save annotation state (vectors)
                annotations_state = None
                is_burnt_in = True
                
            else:
                # Active Elements Mode: Save Clean Image
                # Page 0 is just the RGB version of the raw data (clean)
                # We save vectors in metadata to restore them.
                rgb_data = np.stack((gray_data,)*3, axis=-1)
                page0_data = rgb_data
                
                annotations_state = self.canvas.get_annotations_state()
                is_burnt_in = False
            
            # Extract original metadata (Zeiss tag 34118)
            extratags = []
            with tifffile.TiffFile(self.current_file_path) as tif:
                page = tif.pages[0]
                if 34118 in page.tags:
                    tag = page.tags[34118]
                    # Read raw bytes
                    tif.filehandle.seek(tag.valueoffset)
                    raw_data = tif.filehandle.read(tag.count)
                    # (code, dtype, count, value, writeonce)
                    extratags.append((34118, 's', len(raw_data), raw_data, True))
            
            # Prepare description with measurements and annotation state
            measurements = self.canvas.get_measurements_data()
            
            description_dict = {
                "description": "Annotated Image",
                "measurements": measurements,
                "is_burnt_in": is_burnt_in
            }
            
            if annotations_state:
                description_dict["annotations"] = annotations_state
                
            description_json = json.dumps(description_dict)
            
            # Save as Single-page TIFF
            # Page 0: Annotated/Clean RGB (for viewing) - with metadata
            with tifffile.TiffWriter(file_path) as tif:
                tif.write(page0_data, photometric='rgb', description=description_json, extratags=extratags)
                
            self.status_bar.showMessage(f"Saved: Page 0 to {file_path}")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error saving: {str(e)}")

    def closeEvent(self, event):
        event.accept()

