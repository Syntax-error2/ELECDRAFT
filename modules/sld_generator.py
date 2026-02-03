# modules/sld_generator.py
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QPointF


class SLDGenerator:
    @staticmethod
    def draw_diagram(painter, items):
        """Draws a vertical SLD based on canvas items."""
        painter.setPen(QPen(Qt.black, 2))
        start_y = 50
        x_center = 200

        # Draw Main Service Entrance Line
        painter.drawLine(x_center, 10, x_center, start_y)
        painter.drawText(x_center + 10, 30, "Utility Source")

        # Draw Main Breaker (Rectangle)
        painter.drawRect(x_center - 15, start_y, 30, 40)
        painter.drawText(x_center + 20, start_y + 25, "Main Breaker")

        # Draw Branch Circuits
        current_y = start_y + 80
        for i, item in enumerate(items):
            if hasattr(item, 'va'):  # Ensure it's an electrical component
                # Horizontal branch line
                painter.drawLine(x_center, current_y, x_center + 50, current_y)
                # Symbol for load
                painter.drawEllipse(x_center + 50, current_y - 10, 20, 20)
                painter.drawText(x_center + 80, current_y + 5, f"CKT {i + 1}: {item.name}")
                current_y += 50