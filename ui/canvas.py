import heapq
import os
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem,
                               QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem,
                               QGraphicsPixmapItem, QGraphicsRectItem, QFileDialog)
from PySide6.QtGui import QBrush, QColor, QPen, QPainter, QFont, QPixmap, QWheelEvent, QImage
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QObject
from PySide6.QtSvgWidgets import QGraphicsSvgItem


class CanvasSignals(QObject):
    """Bridge for custom signals within the GraphicsScene."""
    circuit_updated = Signal()


class RoomItem(QGraphicsRectItem):
    """NEW: A visual rectangle that groups components for load density analysis."""

    def __init__(self, name, rect):
        super().__init__(rect)
        self.name = name
        self.is_room_rect = True
        self.setZValue(-1.5)
        self.setPen(QPen(QColor("#00e5ff"), 2, Qt.DashLine))
        self.setBrush(QColor(0, 229, 255, 25))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        self.label = QGraphicsTextItem(self.name, self)
        self.label.setDefaultTextColor(QColor("#00e5ff"))
        self.label.setFont(QFont("Segoe UI", 10, QFont.Bold))


class WireItem(QGraphicsLineItem):
    """A dynamic wire with A* Pathfinding to avoid walls/obstacles."""

    def __init__(self, start_item, end_item, canvas, color="#34e7e4"):
        super().__init__()
        self.start_item = start_item
        self.end_item = end_item
        self.canvas = canvas  # Reference to access obstacle_map
        self.base_color = QColor(color)
        self.is_feeder_line = "Feeder" in [start_item.comp_type, end_item.comp_type]
        self.setZValue(-1)
        self.path_points = []
        self.update_position()

    def update_position(self):
        p1 = self.start_item.scenePos() + QPointF(20, 20)
        p2 = self.end_item.scenePos() + QPointF(20, 20)

        # Calculate Smart Path using A*
        self.path_points = self.calculate_astar_path(p1, p2)

        # Required to update the bounding box for the QGraphicsItem
        self.prepareGeometryChange()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

    def calculate_astar_path(self, start, end):
        """Finds an orthogonal path avoiding dark pixels (walls)."""
        grid = 20
        # Round to grid
        s_node = (round(start.x() / grid) * grid, round(start.y() / grid) * grid)
        e_node = (round(end.x() / grid) * grid, round(end.y() / grid) * grid)

        # If no floorplan, use simple orthogonal bend
        if not self.canvas.obstacle_map:
            return [start, QPointF(e_node[0], s_node[1]), end]

        queue = [(0, s_node)]
        came_from = {s_node: None}
        cost_so_far = {s_node: 0}

        while queue:
            _, current = heapq.heappop(queue)
            if current == e_node: break

            for dx, dy in [(grid, 0), (-grid, 0), (0, grid), (0, -grid)]:
                nxt = (current[0] + dx, current[1] + dy)

                # Check if 'nxt' is a wall
                if self.canvas.is_wall_at(QPointF(nxt[0], nxt[1])):
                    continue

                new_cost = cost_so_far[current] + grid
                if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                    cost_so_far[nxt] = new_cost
                    priority = new_cost + abs(e_node[0] - nxt[0]) + abs(e_node[1] - nxt[1])
                    heapq.heappush(queue, (priority, nxt))
                    came_from[nxt] = current

        # Reconstruct path
        path = []
        curr = e_node
        if curr not in came_from: return [start, end]  # Fallback
        while curr is not None:
            path.append(QPointF(curr[0], curr[1]))
            curr = came_from[curr]
        path.reverse()
        return path

    def paint(self, painter, option, widget):
        glow_width = 10 if self.is_feeder_line else 6
        core_width = 4 if self.is_feeder_line else 2

        for i in range(len(self.path_points) - 1):
            p1, p2 = self.path_points[i], self.path_points[i + 1]
            glow_color = QColor(self.base_color)
            glow_color.setAlpha(60)
            painter.setPen(QPen(glow_color, glow_width))
            painter.drawLine(p1, p2)
            painter.setPen(QPen(self.base_color, core_width, Qt.SolidLine))
            painter.drawLine(p1, p2)


class ElectricalComponent(QGraphicsSvgItem):
    def __init__(self, name, data, pos):
        default_svg = "assets/symbols/feeder.svg" if data.get("type") == "Feeder" else "assets/symbols/generic.svg"
        symbol_path = data.get("symbol", default_svg)
        super().__init__(symbol_path)

        self.name = name
        self.va = data.get("va", 0)
        self.comp_type = data.get("type", "General")
        self.is_continuous = data.get("is_continuous", False)
        self.connections = []
        self.wires = []

        self.setScale(0.4)
        self.setPos(pos)
        self.setZValue(10)
        self.setFlags(
            QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem(self)
        self.label.setScale(2.5)
        self.label.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.label.setDefaultTextColor(QColor("#00e5ff"))
        self.label.setPos(0, 110)
        self.update_label_text()

    def paint(self, painter, option, widget):
        if not self.renderer().isValid():
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(QColor("#00e5ff"), 4)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(0, 229, 255, 40)))
            rect = QRectF(0, 0, 100, 100)
            painter.drawRect(rect)
            painter.drawLine(0, 100, 100, 0)
        else:
            super().paint(painter, option, widget)

        if self.isSelected():
            painter.setPen(QPen(Qt.white, 2, Qt.DashLine))
            painter.drawRect(self.boundingRect().adjusted(-5, -5, 5, 5))

    def update_label_text(self):
        label_str = f"{self.name}" if self.comp_type == "Feeder" else f"{self.name}\n{self.va}VA"
        self.label.setPlainText(label_str)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            new_pos = value
            grid_size = 20
            new_pos.setX(round(new_pos.x() / grid_size) * grid_size)
            new_pos.setY(round(new_pos.y() / grid_size) * grid_size)
            for wire in self.wires:
                wire.update_position()
            return new_pos
        return super().itemChange(change, value)

    def update_data(self, new_name, new_va):
        self.name = new_name
        self.va = int(new_va or 0)
        self.update_label_text()

    def add_connection(self, other_item):
        if other_item and other_item not in self.connections:
            self.connections.append(other_item)
            return True
        return False


class DesignCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 5000, 5000)
        self.setScene(self.scene)
        self.signals = CanvasSignals()
        self.setBackgroundBrush(QBrush(QColor("#0d0f14")))
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.grid_size = 20
        self.wire_mode = False
        self.temp_line = None
        self.start_item = None
        self.floorplan_item = None
        self.obstacle_map = None

    def load_cad_layout(self, dxf_path):
        """Processes the DXF file to create a visual and analytical background."""
        try:
            # Ensure output directory exists
            temp_png = os.path.join("assets", "templates", "processed_view.png")
            os.makedirs(os.path.dirname(temp_png), exist_ok=True)

            print(f"Loading DXF: {dxf_path}")

            # Read the DXF file
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            # Get the bounding box of the drawing to calculate proper figure size
            try:
                # Calculate extents for better sizing
                bbox = ezdxf.bbox.extents(msp)
                print(f"DXF Extents: {bbox}")

                # Calculate aspect ratio
                width = bbox.extmax.x - bbox.extmin.x
                height = bbox.extmax.y - bbox.extmin.y
                aspect_ratio = width / height if height > 0 else 1.0

                # Set figure size based on aspect ratio (maintaining reasonable dimensions)
                if aspect_ratio > 1.5:
                    fig_width, fig_height = 20, 20 / aspect_ratio
                elif aspect_ratio < 0.67:
                    fig_width, fig_height = 20 * aspect_ratio, 20
                else:
                    fig_width, fig_height = 20, 20

            except Exception as e:
                print(f"Could not calculate extents: {e}, using default size")
                fig_width, fig_height = 20, 20
                aspect_ratio = 1.0

            # Create the rendering context
            ctx = RenderContext(doc)

            # Create matplotlib figure with proper sizing
            fig = plt.figure(figsize=(fig_width, fig_height), facecolor='white')
            ax = fig.add_axes([0, 0, 1, 1])  # Full figure, no margins
            ax.set_aspect('equal')

            # Remove axes
            ax.axis('off')
            ax.set_facecolor('white')

            # Render the DXF
            out = MatplotlibBackend(ax)
            Frontend(ctx, out).draw_layout(msp, finalize=True)

            # Save with high DPI for quality
            print(f"Saving rendered image to: {temp_png}")
            fig.savefig(temp_png,
                        dpi=200,  # Reduced from 300 for better performance
                        bbox_inches='tight',
                        pad_inches=0.1,
                        facecolor='white',
                        edgecolor='none')
            plt.close(fig)

            # Verify file was created
            if not os.path.exists(temp_png):
                print("ERROR: PNG file was not created!")
                return False

            print(f"Successfully saved PNG: {os.path.getsize(temp_png)} bytes")

            # Load the template into canvas
            self.set_template(temp_png)

            print("DXF import completed successfully")
            return True

        except Exception as e:
            print(f"CAD Conversion Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def set_template(self, image_path):
        """Load an image as the canvas background template."""
        print(f"Loading template: {image_path}")

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print("ERROR: Failed to load pixmap from image!")
            return

        print(f"Loaded pixmap: {pixmap.width()}x{pixmap.height()}")

        # Remove existing floorplan if present
        if self.floorplan_item:
            self.scene.removeItem(self.floorplan_item)
            self.floorplan_item = None

        # Create new floorplan item
        self.floorplan_item = QGraphicsPixmapItem(pixmap)
        self.floorplan_item.setZValue(-2)  # Behind everything
        self.floorplan_item.setAcceptedMouseButtons(Qt.NoButton)  # Not interactive

        # Position at origin
        self.floorplan_item.setPos(0, 0)

        # Add to scene
        self.scene.addItem(self.floorplan_item)

        # Update scene boundaries to match the image
        image_rect = self.floorplan_item.boundingRect()
        print(f"Image bounding rect: {image_rect}")

        # Expand scene slightly beyond image
        margin = 500
        self.scene.setSceneRect(
            image_rect.adjusted(-margin, -margin, margin, margin)
        )

        # Cache image for wall detection
        self.obstacle_map = pixmap.toImage()
        print(f"Obstacle map cached: {self.obstacle_map.width()}x{self.obstacle_map.height()}")

        # Fit the view to show the entire floorplan
        self.fitInView(self.floorplan_item, Qt.KeepAspectRatio)

        # Add a small zoom out for context
        self.scale(0.9, 0.9)

        # Center the view
        self.centerOn(self.floorplan_item)

        print("Template loaded and view adjusted")

    def is_wall_at(self, scene_pos):
        """Checks if a point is dark (wall) or bright (floor)."""
        if not self.obstacle_map or not self.floorplan_item:
            return False

        # Convert scene position to local floorplan coordinates
        local_p = self.floorplan_item.mapFromScene(scene_pos)
        x, y = int(local_p.x()), int(local_p.y())

        # Check bounds
        if 0 <= x < self.obstacle_map.width() and 0 <= y < self.obstacle_map.height():
            # Dark pixels (low lightness) = walls
            pixel_color = self.obstacle_map.pixelColor(x, y)
            lightness = pixel_color.lightness()
            return lightness < 120  # Threshold for wall detection

        return False

    def run_load_analysis(self):
        """Aggregates VA loads within RoomItem boundaries."""
        results = ""
        total_va = 0

        for item in self.scene.items():
            if isinstance(item, RoomItem):
                room_total = 0
                # Finds components physically inside the RoomItem rectangle
                for collided in self.scene.collidingItems(item):
                    if isinstance(collided, ElectricalComponent):
                        room_total += collided.va

                results += f"{item.name}: {room_total} VA\n"
                total_va += room_total

        results += f"\nTOTAL CONNECTED LOAD: {total_va} VA"
        return results

    def drawBackground(self, painter, rect):
        """Draw the grid background."""
        super().drawBackground(painter, rect)

        # Only draw grid if we're zoomed in enough
        if self.transform().m11() < 0.5:  # Skip grid when zoomed out
            return

        painter.setPen(QPen(QColor("#1c222d"), 0.5))

        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)

        # Draw vertical lines
        for x in range(left, int(rect.right()), self.grid_size):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))

        # Draw horizontal lines
        for y in range(top, int(rect.bottom()), self.grid_size):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def toggle_wire_mode(self, enabled):
        """Toggle wire drawing mode."""
        self.wire_mode = enabled
        self.setDragMode(QGraphicsView.NoDrag if enabled else QGraphicsView.RubberBandDrag)
        self.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)

    def get_component_at(self, pos):
        """Find an ElectricalComponent at the given view position."""
        scene_pos = self.mapToScene(pos)

        for item in self.scene.items(scene_pos):
            # Check if item is component or child of component
            temp = item
            while temp:
                if isinstance(temp, ElectricalComponent):
                    return temp
                temp = temp.parentItem()

        return None

    def mousePressEvent(self, event):
        """Handle mouse press for wire drawing."""
        if self.wire_mode and event.button() == Qt.LeftButton:
            item = self.get_component_at(event.pos())
            if item:
                self.start_item = item
                start_p = item.scenePos() + QPointF(20, 20)

                self.temp_line = QGraphicsLineItem(start_p.x(), start_p.y(), start_p.x(), start_p.y())
                self.temp_line.setPen(QPen(QColor("#00e5ff"), 2, Qt.DashLine))
                self.temp_line.setZValue(10)
                self.scene.addItem(self.temp_line)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for wire drawing preview."""
        if self.wire_mode and self.temp_line:
            end_pos = self.mapToScene(event.pos())
            self.temp_line.setLine(
                self.temp_line.line().x1(),
                self.temp_line.line().y1(),
                end_pos.x(),
                end_pos.y()
            )

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to finalize wire connection."""
        if self.wire_mode and self.temp_line:
            end_item = self.get_component_at(event.pos())

            if end_item and end_item != self.start_item:
                # Create the wire with pathfinding
                new_wire = WireItem(self.start_item, end_item, self)
                self.scene.addItem(new_wire)

                # Track wires in components
                self.start_item.wires.append(new_wire)
                end_item.wires.append(new_wire)

                # Emit signal for updates
                self.signals.circuit_updated.emit()

            # Remove temporary line
            self.scene.removeItem(self.temp_line)
            self.temp_line = None

        super().mouseReleaseEvent(event)

    def add_component(self, name, data):
        """Add a new electrical component to the canvas."""
        # Get center of current view
        view_center = self.viewport().rect().center()
        scene_center = self.mapToScene(view_center)

        # Create component
        item = ElectricalComponent(name, data, scene_center)
        self.scene.addItem(item)

        # Emit update signal
        self.signals.circuit_updated.emit()

        return item

    def add_room(self, name):
        """Add a new room boundary rectangle."""
        center = self.mapToScene(self.viewport().rect().center())
        room = RoomItem(name, QRectF(0, 0, 300, 300))
        room.setPos(center)
        self.scene.addItem(room)

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        # Zoom factor
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15

        # Apply zoom
        self.scale(factor, factor)