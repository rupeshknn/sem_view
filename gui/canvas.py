from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QPen, QColor, QFont, QPainter

class MeasurementItem:
    def __init__(self, line_item, text_item, start_point, end_point):
        self.line_item = line_item
        self.text_item = text_item
        self.start_point = start_point
        self.end_point = end_point

class ImageCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag) # Disable default drag to handle manually
        self.setCursor(Qt.CrossCursor)
        
        self.pixmap_item = None
        self.pixel_scale = None # meters per pixel
        
        self.current_line = None
        self.drawing = False
        self.panning = False
        self.last_pan_pos = QPointF()
        self.start_pos = None
        
        self.measurements = []

    def set_image(self, pixmap):
        self.scene.clear()
        self.measurements = []
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(self.pixmap_item.boundingRect())
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def set_scale(self, scale):
        self.pixel_scale = scale

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Start drawing line
            self.drawing = True
            pos = self.mapToScene(event.pos())
            self.start_pos = pos
            self.current_line = QGraphicsLineItem(QLineF(pos, pos))
            pen = QPen(QColor("yellow"))
            pen.setWidth(2)
            # Make pen width constant regardless of zoom
            pen.setCosmetic(True)
            self.current_line.setPen(pen)
            self.scene.addItem(self.current_line)
        elif event.button() == Qt.LeftButton:
            # Start panning
            self.panning = True
            self.last_pan_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing and self.current_line:
            pos = self.mapToScene(event.pos())
            line = self.current_line.line()
            line.setP2(pos)
            self.current_line.setLine(line)
        elif self.panning:
            delta = event.pos() - self.last_pan_pos
            self.last_pan_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing and event.button() == Qt.RightButton:
            self.drawing = False
            if self.current_line:
                end_pos = self.mapToScene(event.pos())
                
                # Calculate distance
                line = self.current_line.line()
                length_px = line.length()
                
                text_content = f"{length_px:.1f} px"
                if self.pixel_scale:
                    length_m = length_px * self.pixel_scale
                    if length_m < 1e-6:
                        text_content = f"{length_m * 1e9:.2f} nm"
                    elif length_m < 1e-3:
                        text_content = f"{length_m * 1e6:.2f} µm"
                    else:
                        text_content = f"{length_m * 1e3:.2f} mm"
                
                # Add text annotation
                text_item = QGraphicsTextItem(text_content)
                text_item.setDefaultTextColor(QColor("yellow"))
                font = QFont()
                font.setBold(True)
                font.setPointSize(10)
                text_item.setFont(font)
                text_item.setPos(end_pos)
                # Scale text to remain readable
                text_item.setScale(1.0 / self.transform().m11())
                self.scene.addItem(text_item)
                
                self.measurements.append(MeasurementItem(self.current_line, text_item, self.start_pos, end_pos))
                self.current_line = None
        elif self.panning and event.button() == Qt.LeftButton:
            self.panning = False
            self.setCursor(Qt.CrossCursor)
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Save the scene pos
        old_pos = self.mapToScene(event.position().toPoint())

        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)

        # Get the new position
        new_pos = self.mapToScene(event.position().toPoint())

        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        
        # Adjust text items scale to keep them readable
        for item in self.scene.items():
            if isinstance(item, QGraphicsTextItem):
                # Reset scale and apply inverse of view scale
                item.setScale(1.0 / self.transform().m11())
