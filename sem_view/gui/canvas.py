from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem, QGraphicsPolygonItem
from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QPen, QColor, QFont, QPainter, QPolygonF

class MeasurementItem:
    def __init__(self, graphics_item, text_item, data):
        self.graphics_item = graphics_item
        self.text_item = text_item
        self.data = data # Store points or other data

class ImageCanvas(QGraphicsView):
    MODE_MEASURE = 0
    MODE_POLYGON = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag) # Disable default drag to handle manually
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        
        self.pixmap_item = None
        self.pixel_scale = None # meters per pixel
        
        self.mode = self.MODE_MEASURE
        
        # Line drawing state
        self.current_line = None
        self.drawing = False
        self.start_pos = None
        
        # Polygon drawing state
        self.polygon_points = []
        self.current_polygon_item = None
        self.temp_line = None
        
        self.panning = False
        self.last_pan_pos = QPointF()
        
        self.measurements = []
        
        # Colors
        self.colors = [
            QColor("#FFFF00"), # Yellow
            QColor("#00FFFF"), # Cyan
            QColor("#FF00FF"), # Magenta
            QColor("#00FF00"), # Lime
            QColor("#FFA500"), # Orange
            QColor("#FF0000"), # Red
            QColor("#00BFFF"), # Deep Sky Blue
            QColor("#FF69B4"), # Hot Pink
        ]
        self.color_index = 0

    def get_next_color(self):
        color = self.colors[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.colors)
        return color
        
    def clear_measurements(self):
        for m in self.measurements:
            self.scene.removeItem(m.graphics_item)
            self.scene.removeItem(m.text_item)
        self.measurements = []
        self.color_index = 0
        self.scene.update()

    def get_measurements_data(self):
        data = []
        for m in self.measurements:
            text = m.text_item.toPlainText()
            # Parse text to get value and unit
            parts = text.split(' ')
            if len(parts) >= 2:
                value = parts[0]
                unit = parts[1]
                
                item_type = "Unknown"
                if isinstance(m.graphics_item, QGraphicsLineItem):
                    item_type = "Distance"
                    color = m.graphics_item.pen().color().name()
                elif isinstance(m.graphics_item, QGraphicsPolygonItem):
                    item_type = "Area"
                    color = m.graphics_item.pen().color().name()
                else:
                    color = "#000000"
                    
                data.append({
                    "type": item_type,
                    "value": value,
                    "unit": unit,
                    "label": text,
                    "color": color
                })
        return data

    def set_mode(self, mode):
        self.mode = mode
        # Reset any active drawing
        self.drawing = False
        self.polygon_points = []
        if self.current_line:
            self.scene.removeItem(self.current_line)
            self.current_line = None
        if self.current_polygon_item:
            self.scene.removeItem(self.current_polygon_item)
            self.current_polygon_item = None
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None

    def set_image(self, pixmap):
        self.scene.clear()
        self.measurements = []
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(self.pixmap_item.boundingRect())
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def set_scale(self, scale):
        self.pixel_scale = scale

    def add_measurement_line(self, start_pos, end_pos, color=None):
        if color is None:
            color = self.colors[self.color_index]
            self.color_index = (self.color_index + 1) % len(self.colors)
            
        line_item = QGraphicsLineItem(QLineF(start_pos, end_pos))
        pen = QPen(color)
        pen.setWidth(2)
        pen.setCosmetic(True)
        line_item.setPen(pen)
        self.scene.addItem(line_item)
        
        # Calculate distance
        line = line_item.line()
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
        text_item.setDefaultTextColor(color)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        text_item.setFont(font)
        text_item.setPos(end_pos)
        # Scale text to remain readable
        text_item.setScale(1.0 / self.transform().m11())
        self.scene.addItem(text_item)
        
        self.measurements.append(MeasurementItem(line_item, text_item, [start_pos, end_pos]))
        return line_item

    def add_measurement_polygon(self, points, color=None):
        if len(points) < 3:
            return None
            
        if color is None:
            color = self.colors[self.color_index]
            self.color_index = (self.color_index + 1) % len(self.colors)
            
        poly_item = QGraphicsPolygonItem(QPolygonF(points))
        pen = QPen(color)
        pen.setWidth(2)
        pen.setCosmetic(True)
        poly_item.setPen(pen)
        brush = QColor(color)
        brush.setAlpha(50)
        poly_item.setBrush(brush)
        self.scene.addItem(poly_item)
        
        # Calculate Area
        area_px = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            area_px += points[i].x() * points[j].y()
            area_px -= points[j].x() * points[i].y()
        area_px = abs(area_px) / 2.0
        
        text_content = f"{area_px:.0f} px²"
        if self.pixel_scale:
            area_m2 = area_px * (self.pixel_scale ** 2)
            if area_m2 < 1e-12:
                text_content = f"{area_m2 * 1e18:.2f} nm²"
            elif area_m2 < 1e-6:
                text_content = f"{area_m2 * 1e12:.2f} µm²"
            else:
                text_content = f"{area_m2 * 1e6:.2f} mm²"
        
        # Add text annotation at center
        center = poly_item.boundingRect().center()
        text_item = QGraphicsTextItem(text_content)
        text_item.setDefaultTextColor(color)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        text_item.setFont(font)
        text_item.setPos(center)
        text_item.setScale(1.0 / self.transform().m11())
        self.scene.addItem(text_item)
        
        self.measurements.append(MeasurementItem(poly_item, text_item, points))
        return poly_item

    def get_annotations_state(self):
        state = []
        for m in self.measurements:
            item_data = {}
            if isinstance(m.graphics_item, QGraphicsLineItem):
                item_data['type'] = 'distance'
                item_data['start'] = [m.data[0].x(), m.data[0].y()]
                item_data['end'] = [m.data[1].x(), m.data[1].y()]
                item_data['color'] = m.graphics_item.pen().color().name()
            elif isinstance(m.graphics_item, QGraphicsPolygonItem):
                item_data['type'] = 'area'
                item_data['points'] = [[p.x(), p.y()] for p in m.data]
                item_data['color'] = m.graphics_item.pen().color().name()
            state.append(item_data)
        return state

    def restore_annotations_state(self, state):
        self.clear_measurements()
        for item_data in state:
            try:
                color = QColor(item_data.get('color', '#FFFF00'))
                if item_data['type'] == 'distance':
                    start = QPointF(item_data['start'][0], item_data['start'][1])
                    end = QPointF(item_data['end'][0], item_data['end'][1])
                    self.add_measurement_line(start, end, color)
                elif item_data['type'] == 'area':
                    points = [QPointF(p[0], p[1]) for p in item_data['points']]
                    self.add_measurement_polygon(points, color)
            except Exception as e:
                print(f"Error restoring annotation: {e}")
                
        # Update color_index based on last measurement to avoid reuse
        if self.measurements:
            last_item = self.measurements[-1]
            last_color = None
            if isinstance(last_item.graphics_item, QGraphicsLineItem):
                last_color = last_item.graphics_item.pen().color()
            elif isinstance(last_item.graphics_item, QGraphicsPolygonItem):
                last_color = last_item.graphics_item.pen().color()
            
            if last_color:
                # Find index in self.colors
                found = False
                for i, color in enumerate(self.colors):
                    # Compare RGB values
                    if color.rgb() == last_color.rgb():
                        self.color_index = (i + 1) % len(self.colors)
                        found = True
                        break
                
                if not found:
                    # Fallback to count
                    self.color_index = len(self.measurements) % len(self.colors)

    def set_annotations_visible(self, visible):
        for m in self.measurements:
            m.graphics_item.setVisible(visible)
            m.text_item.setVisible(visible)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mode == self.MODE_MEASURE:
                if not self.drawing:
                    # Start drawing line
                    self.drawing = True
                    pos = self.mapToScene(event.pos())
                    self.start_pos = pos
                    self.current_line = QGraphicsLineItem(QLineF(pos, pos))
                    
                    # Use current color
                    color = self.colors[self.color_index]
                    pen = QPen(color)
                    pen.setWidth(2)
                    pen.setCosmetic(True)
                    self.current_line.setPen(pen)
                    self.scene.addItem(self.current_line)
                else:
                    # Finish drawing line
                    self.drawing = False
                    if self.current_line:
                        end_pos = self.mapToScene(event.pos())
                        self.scene.removeItem(self.current_line) # Remove temp line
                        self.current_line = None
                        
                        # Add permanent measurement
                        self.add_measurement_line(self.start_pos, end_pos)
                        
            elif self.mode == self.MODE_POLYGON:
                # Add point to polygon
                pos = self.mapToScene(event.pos())
                self.polygon_points.append(pos)
                
                # Update visual polygon
                color = self.colors[self.color_index]
                if not self.current_polygon_item:
                    self.current_polygon_item = QGraphicsPolygonItem(QPolygonF(self.polygon_points))
                    pen = QPen(color)
                    pen.setWidth(2)
                    pen.setCosmetic(True)
                    self.current_polygon_item.setPen(pen)
                    brush = QColor(color)
                    brush.setAlpha(50)
                    self.current_polygon_item.setBrush(brush)
                    self.scene.addItem(self.current_polygon_item)
                else:
                    self.current_polygon_item.setPolygon(QPolygonF(self.polygon_points))
        elif event.button() == Qt.RightButton:
            if self.mode == self.MODE_POLYGON:
                # Add the current point as the final vertex
                pos = self.mapToScene(event.pos())
                self.polygon_points.append(pos)
                self.finish_polygon()
        elif event.button() == Qt.MiddleButton:
            # Start panning
            self.panning = True
            self.last_pan_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        
        if self.mode == self.MODE_MEASURE and self.drawing and self.current_line:
            line = self.current_line.line()
            line.setP2(pos)
            self.current_line.setLine(line)
        elif self.mode == self.MODE_POLYGON and self.polygon_points:
            # Draw temp line from last point to cursor
            if not self.temp_line:
                self.temp_line = QGraphicsLineItem(QLineF(self.polygon_points[-1], pos))
                color = self.colors[self.color_index]
                pen = QPen(color)
                pen.setStyle(Qt.DashLine)
                pen.setCosmetic(True)
                self.temp_line.setPen(pen)
                self.scene.addItem(self.temp_line)
            else:
                self.temp_line.setLine(QLineF(self.polygon_points[-1], pos))
                
        if self.panning:
            delta = event.pos() - self.last_pan_pos
            self.last_pan_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        else:
            super().mouseMoveEvent(event)
            


    def finish_polygon(self):
        if len(self.polygon_points) < 3:
            return
            
        # Remove temp line
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
            
        # Remove visual polygon (we will recreate it as permanent)
        if self.current_polygon_item:
            self.scene.removeItem(self.current_polygon_item)
            self.current_polygon_item = None
            
        # Add permanent measurement
        self.add_measurement_polygon(self.polygon_points)
        
        # Reset
        self.polygon_points = []

    def mouseReleaseEvent(self, event):
        if self.panning and event.button() == Qt.MiddleButton:
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
