"""
sld_generator.py – Professional Single-Line Diagram Generator
===============================================================
PEC-compliant electrical symbology with enterprise-grade rendering.

Features:
  • Automatic intelligent layout
  • Professional electrical symbols
  • Load balancing visualization
  • Color-coded wire types
  • Comprehensive annotations
  • Export-ready quality
"""

from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
    QLinearGradient, QRadialGradient, QPolygonF
)
from PySide6.QtCore import Qt, QPointF, QRectF
import math


# ==========================================================================
# PROFESSIONAL COLOR PALETTE  (matching main UI)
# ==========================================================================
class SLDColors:
    """Unified color system for SLD diagrams."""

    # Backgrounds
    BG_CANVAS = QColor("#FFFFFF")  # white for print
    BG_DARK = QColor("#0E1013")  # dark mode option

    # Lines & Borders
    LINE_MAIN = QColor("#1A1F26")  # main bus/feeder
    LINE_BRANCH = QColor("#2D3646")  # branch circuits
    LINE_GROUND = QColor("#2EA043")  # grounding

    # Symbols
    BREAKER = QColor("#1A1F26")  # breaker outline
    PANEL = QColor("#161A1F")  # panel fill
    LOAD_LIGHT = QColor("#F1C40F")  # lighting loads
    LOAD_RECEPT = QColor("#00D9FF")  # receptacle loads
    LOAD_MOTOR = QColor("#FF6B81")  # motor loads
    LOAD_AC = QColor("#DA3633")  # AC/HVAC loads

    # Text
    TEXT_PRIMARY = QColor("#0E1013")  # labels
    TEXT_SECONDARY = QColor("#636C76")  # annotations
    TEXT_ACCENT = QColor("#00D9FF")  # highlights

    # Grid
    GRID_MAJOR = QColor("#E1E4E8")  # major grid
    GRID_MINOR = QColor("#F6F8FA")  # minor grid


# ==========================================================================
# ELECTRICAL SYMBOL LIBRARY
# ==========================================================================
class ElectricalSymbols:
    """Professional PEC-compliant electrical symbols."""

    @staticmethod
    def draw_main_breaker(painter: QPainter, x: float, y: float, rating: str, width: float = 60) -> None:
        """Main service disconnect breaker."""
        h = 80

        # Outer housing
        rect = QRectF(x - width / 2, y, width, h)

        # Gradient fill
        grad = QLinearGradient(x - width / 2, y, x - width / 2, y + h)
        grad.setColorAt(0.0, QColor("#F6F8FA"))
        grad.setColorAt(1.0, QColor("#E1E4E8"))

        painter.setBrush(grad)
        painter.setPen(QPen(SLDColors.BREAKER, 2))
        painter.drawRect(rect)

        # Internal contacts (two parallel lines)
        contact_y = y + h * 0.3
        painter.setPen(QPen(SLDColors.BREAKER, 3))
        painter.drawLine(x - 15, contact_y, x + 15, contact_y)
        painter.drawLine(x - 15, contact_y + 8, x + 15, contact_y + 8)

        # Rating label
        painter.setPen(SLDColors.TEXT_PRIMARY)
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.drawText(rect.adjusted(0, h - 25, 0, 0), Qt.AlignCenter, rating)

        # "MAIN" label
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(rect.adjusted(0, 8, 0, 0), Qt.AlignCenter, "MAIN")

    @staticmethod
    def draw_branch_breaker(painter: QPainter, x: float, y: float, rating: str, pole: int = 1) -> None:
        """Branch circuit breaker (1-pole, 2-pole, 3-pole)."""
        w = 30 if pole == 1 else 45
        h = 35

        rect = QRectF(x - w / 2, y - h / 2, w, h)

        # Fill based on pole count
        if pole == 1:
            painter.setBrush(QColor("#FFFFFF"))
        elif pole == 2:
            painter.setBrush(QColor("#F6F8FA"))
        else:
            painter.setBrush(QColor("#E1E4E8"))

        painter.setPen(QPen(SLDColors.BREAKER, 1.5))
        painter.drawRect(rect)

        # Internal representation
        if pole >= 2:
            # Double lines for 2P
            painter.drawLine(x - 10, y - 8, x + 10, y - 8)
            painter.drawLine(x - 10, y + 8, x + 10, y + 8)
        else:
            # Single line for 1P
            painter.drawLine(x - 10, y, x + 10, y)

        # Rating
        painter.setFont(QFont("Consolas", 7, QFont.Bold))
        painter.setPen(SLDColors.TEXT_PRIMARY)
        painter.drawText(rect, Qt.AlignCenter, f"{rating}A")

    @staticmethod
    def draw_panel(painter: QPainter, x: float, y: float, name: str, width: float = 100) -> None:
        """Distribution panel symbol."""
        h = 60
        rect = QRectF(x - width / 2, y, width, h)

        # Panel housing
        grad = QLinearGradient(x - width / 2, y, x + width / 2, y)
        grad.setColorAt(0.0, QColor("#1A1F26"))
        grad.setColorAt(0.5, QColor("#161A1F"))
        grad.setColorAt(1.0, QColor("#1A1F26"))

        painter.setBrush(grad)
        painter.setPen(QPen(SLDColors.BREAKER, 2))
        painter.drawRect(rect)

        # Bus bars (three vertical lines)
        bus_spacing = width / 4
        painter.setPen(QPen(QColor("#00D9FF"), 2))
        for i in range(3):
            bx = x - width / 2 + bus_spacing * (i + 1)
            painter.drawLine(bx, y + 15, bx, y + h - 15)

        # Label
        painter.setPen(QColor("#ECEFF4"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(rect.adjusted(0, h - 20, 0, 0), Qt.AlignCenter, name)

    @staticmethod
    def draw_load_symbol(painter: QPainter, x: float, y: float, load_type: str, size: float = 20) -> None:
        """Load symbols (lighting, receptacle, motor, AC)."""
        if "Light" in load_type or "Emergency" in load_type:
            # Circle with cross (lighting)
            painter.setBrush(SLDColors.LOAD_LIGHT)
            painter.setPen(QPen(SLDColors.BREAKER, 1.5))
            painter.drawEllipse(QPointF(x, y), size / 2, size / 2)
            painter.drawLine(x - size / 3, y, x + size / 3, y)
            painter.drawLine(x, y - size / 3, x, y + size / 3)

        elif "Duplex" in load_type or "Outlet" in load_type or "GFCI" in load_type:
            # Square (receptacle)
            rect = QRectF(x - size / 2, y - size / 2, size, size)
            painter.setBrush(SLDColors.LOAD_RECEPT)
            painter.setPen(QPen(SLDColors.BREAKER, 1.5))
            painter.drawRect(rect)
            # Two vertical slots
            painter.setPen(QPen(SLDColors.BREAKER, 2))
            painter.drawLine(x - 4, y - 6, x - 4, y + 6)
            painter.drawLine(x + 4, y - 6, x + 4, y + 6)

        elif "Motor" in load_type or "Pump" in load_type:
            # Circle with M (motor)
            painter.setBrush(SLDColors.LOAD_MOTOR)
            painter.setPen(QPen(SLDColors.BREAKER, 1.5))
            painter.drawEllipse(QPointF(x, y), size / 2, size / 2)
            painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
            painter.setPen(SLDColors.TEXT_PRIMARY)
            painter.drawText(QRectF(x - size / 2, y - size / 2, size, size), Qt.AlignCenter, "M")

        elif "AC" in load_type:
            # Diamond (HVAC)
            points = QPolygonF([
                QPointF(x, y - size / 2),
                QPointF(x + size / 2, y),
                QPointF(x, y + size / 2),
                QPointF(x - size / 2, y)
            ])
            painter.setBrush(SLDColors.LOAD_AC)
            painter.setPen(QPen(SLDColors.BREAKER, 1.5))
            painter.drawPolygon(points)

        else:
            # Generic (circle)
            painter.setBrush(QColor("#8B949E"))
            painter.setPen(QPen(SLDColors.BREAKER, 1.5))
            painter.drawEllipse(QPointF(x, y), size / 2, size / 2)

    @staticmethod
    def draw_wire(painter: QPainter, x1: float, y1: float, x2: float, y2: float,
                  wire_type: str = "branch", label: str = "") -> None:
        """Draw wire/conductor with proper styling."""
        if wire_type == "main":
            pen = QPen(SLDColors.LINE_MAIN, 3, Qt.SolidLine)
        elif wire_type == "feeder":
            pen = QPen(SLDColors.LINE_MAIN, 2.5, Qt.SolidLine)
        elif wire_type == "ground":
            pen = QPen(SLDColors.LINE_GROUND, 2, Qt.DashLine)
        else:  # branch
            pen = QPen(SLDColors.LINE_BRANCH, 1.5, Qt.SolidLine)

        painter.setPen(pen)
        painter.drawLine(x1, y1, x2, y2)

        # Wire size label
        if label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            painter.setFont(QFont("Consolas", 7))
            painter.setPen(SLDColors.TEXT_SECONDARY)
            painter.drawText(QPointF(mid_x + 5, mid_y - 5), label)


# ==========================================================================
# INTELLIGENT LAYOUT ENGINE
# ==========================================================================
class SLDLayoutEngine:
    """Automatic layout calculator for SLD diagrams."""

    def __init__(self, canvas_width: int = 800, canvas_height: int = 1000) -> None:
        self.canvas_w = canvas_width
        self.canvas_h = canvas_height
        self.margin = 80
        self.x_center = canvas_width // 2

        # Layout zones
        self.utility_y = self.margin
        self.main_breaker_y = self.utility_y + 80
        self.panel_y = self.main_breaker_y + 140
        self.circuits_start_y = self.panel_y + 120
        self.circuit_spacing = 70

    def get_circuit_position(self, index: int, total: int) -> tuple[float, float]:
        """Calculate position for a branch circuit."""
        y = self.circuits_start_y + index * self.circuit_spacing

        # Alternate left/right for cleaner layout
        if index % 2 == 0:
            x = self.x_center + 120
        else:
            x = self.x_center - 120

        return x, y

    def estimate_height(self, circuit_count: int) -> int:
        """Estimate total diagram height."""
        return self.circuits_start_y + (circuit_count * self.circuit_spacing) + self.margin


# ==========================================================================
# MAIN SLD GENERATOR
# ==========================================================================
class SLDGenerator:
    """Professional single-line diagram generator."""

    def __init__(self, dark_mode: bool = False) -> None:
        self.dark_mode = dark_mode
        self.layout = SLDLayoutEngine()
        self.symbols = ElectricalSymbols()

    # ══════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════════
    @staticmethod
    def draw_diagram(painter: QPainter, items: list, project_data: dict = None) -> None:
        """Main entry point for drawing SLD. Compatible with existing code."""
        generator = SLDGenerator()
        generator.render(painter, items, project_data or {})

    def render(self, painter: QPainter, items: list, project_data: dict) -> None:
        """Render complete SLD diagram."""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # Background
        if self.dark_mode:
            painter.fillRect(0, 0, self.layout.canvas_w, self.layout.canvas_h, SLDColors.BG_DARK)
        else:
            painter.fillRect(0, 0, self.layout.canvas_w, self.layout.canvas_h, SLDColors.BG_CANVAS)

        # ── 1. Title block ────────────────────────────────────────────
        self._draw_title_block(painter, project_data)

        # ── 2. Utility source ─────────────────────────────────────────
        self._draw_utility_source(painter)

        # ── 3. Main service disconnect ────────────────────────────────
        total_va = sum(item.get("va", 0) for item in items)
        main_amps = int(total_va / project_data.get("system_voltage", 230) * 1.25)
        main_rating = self._round_breaker(main_amps)

        self._draw_main_service(painter, main_rating)

        # ── 4. Main panel ─────────────────────────────────────────────
        self._draw_main_panel(painter, project_data.get("name", "MAIN PANEL"))

        # ── 5. Branch circuits ────────────────────────────────────────
        self._draw_branch_circuits(painter, items, project_data)

        # ── 6. Legend ─────────────────────────────────────────────────
        self._draw_legend(painter)

        # ── 7. Notes ──────────────────────────────────────────────────
        self._draw_notes(painter, project_data)

    # ══════════════════════════════════════════════════════════════════
    # INTERNAL RENDERING METHODS
    # ══════════════════════════════════════════════════════════════════
    def _draw_title_block(self, painter: QPainter, project_data: dict) -> None:
        """Professional title block at top."""
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        painter.setPen(SLDColors.TEXT_PRIMARY)
        painter.drawText(
            QRectF(self.layout.margin, 20, self.layout.canvas_w - 2 * self.layout.margin, 30),
            Qt.AlignCenter,
            "SINGLE LINE DIAGRAM"
        )

        # Project info
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(SLDColors.TEXT_SECONDARY)
        info_y = 55
        info_x = self.layout.margin

        painter.drawText(info_x, info_y, f"PROJECT: {project_data.get('name', 'N/A')}")
        painter.drawText(info_x + 300, info_y, f"VOLTAGE: {project_data.get('system_voltage', 230)}V / 1Ø")
        painter.drawText(info_x + 500, info_y, f"STANDARD: {project_data.get('standard', 'PEC 2017')}")

    def _draw_utility_source(self, painter: QPainter) -> None:
        """Utility connection point."""
        x = self.layout.x_center
        y = self.layout.utility_y

        # Arrow pointing down
        arrow = QPolygonF([
            QPointF(x, y),
            QPointF(x - 10, y - 20),
            QPointF(x + 10, y - 20)
        ])
        painter.setBrush(SLDColors.TEXT_ACCENT)
        painter.setPen(QPen(SLDColors.BREAKER, 1.5))
        painter.drawPolygon(arrow)

        # Label
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.setPen(SLDColors.TEXT_PRIMARY)
        painter.drawText(QPointF(x + 15, y - 5), "UTILITY")

        # Vertical line to main
        self.symbols.draw_wire(painter, x, y, x, self.layout.main_breaker_y, "main")

    def _draw_main_service(self, painter: QPainter, rating: int) -> None:
        """Main service disconnect breaker."""
        x = self.layout.x_center
        y = self.layout.main_breaker_y

        self.symbols.draw_main_breaker(painter, x, y, f"{rating}A")

        # Wire to panel
        self.symbols.draw_wire(
            painter, x, y + 80, x, self.layout.panel_y, "feeder", f"#{self._get_feeder_wire(rating)}"
        )

    def _draw_main_panel(self, painter: QPainter, name: str) -> None:
        """Main distribution panel."""
        x = self.layout.x_center
        y = self.layout.panel_y

        self.symbols.draw_panel(painter, x, y, name)

    def _draw_branch_circuits(self, painter: QPainter, items: list, project_data: dict) -> None:
        """All branch circuits with automatic layout."""
        panel_x = self.layout.x_center
        panel_bottom = self.layout.panel_y + 60

        system_v = project_data.get("system_voltage", 230)

        for idx, item in enumerate(items):
            # Calculate position
            circuit_x, circuit_y = self.layout.get_circuit_position(idx, len(items))
            is_left = (idx % 2 == 1)

            # ── Branch breaker ────────────────────────────────────────
            va = item.get("va", 0)
            amps = va / system_v if system_v > 0 else 0
            breaker_rating = self._round_breaker(int(amps * 1.25))
            wire_size = item.get("wire", "2.0mm²")

            # Breaker position (on the panel edge)
            breaker_x = panel_x - 50 if is_left else panel_x + 50
            breaker_y = circuit_y

            self.symbols.draw_branch_breaker(painter, breaker_x, breaker_y, str(breaker_rating))

            # ── Wire from panel to breaker ───────────────────────────
            painter.setPen(QPen(SLDColors.LINE_BRANCH, 1.5))
            painter.drawLine(panel_x, panel_bottom, breaker_x, breaker_y)

            # ── Wire from breaker to load ────────────────────────────
            self.symbols.draw_wire(
                painter, breaker_x, breaker_y, circuit_x, circuit_y, "branch", wire_size
            )

            # ── Load symbol ───────────────────────────────────────────
            self.symbols.draw_load_symbol(painter, circuit_x, circuit_y, item.get("name", "Load"))

            # ── Circuit label ─────────────────────────────────────────
            label_x = circuit_x + 25
            label_y = circuit_y

            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.setPen(SLDColors.TEXT_PRIMARY)
            painter.drawText(QPointF(label_x, label_y - 5), f"CKT {idx + 1}")

            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(SLDColors.TEXT_SECONDARY)
            painter.drawText(QPointF(label_x, label_y + 8), item.get("name", "Load"))
            painter.drawText(QPointF(label_x, label_y + 20), f"{va} VA")

    def _draw_legend(self, painter: QPainter) -> None:
        """Symbol legend in bottom-left corner."""
        legend_x = self.layout.margin
        legend_y = self.layout.canvas_h - 180

        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.setPen(SLDColors.TEXT_PRIMARY)
        painter.drawText(legend_x, legend_y, "LEGEND")

        legend_y += 25

        symbols_info = [
            ("Lighting", "Light"),
            ("Receptacle", "Duplex"),
            ("Motor Load", "Motor"),
            ("AC/HVAC", "AC"),
        ]

        painter.setFont(QFont("Segoe UI", 8))
        for label, stype in symbols_info:
            self.symbols.draw_load_symbol(painter, legend_x + 10, legend_y, stype, 16)
            painter.drawText(legend_x + 30, legend_y + 5, label)
            legend_y += 25

    def _draw_notes(self, painter: QPainter, project_data: dict) -> None:
        """General notes at bottom."""
        notes_x = self.layout.margin + 200
        notes_y = self.layout.canvas_h - 180

        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.setPen(SLDColors.TEXT_PRIMARY)
        painter.drawText(notes_x, notes_y, "NOTES")

        notes_y += 20

        notes = [
            "1. All wiring per PEC 2017 standards",
            "2. Breaker ratings are minimum; verify with load calculations",
            "3. Wire sizes shown are conductor size (mm²)",
            f"4. System voltage: {project_data.get('system_voltage', 230)}V single-phase",
            "5. All circuits include equipment grounding conductor",
        ]

        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(SLDColors.TEXT_SECONDARY)
        for note in notes:
            painter.drawText(notes_x, notes_y, note)
            notes_y += 18

    # ══════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ══════════════════════════════════════════════════════════════════
    @staticmethod
    def _round_breaker(amps: float) -> int:
        """Round to standard breaker size."""
        standard_sizes = [15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 125, 150, 175, 200, 225, 250, 300, 400]
        for size in standard_sizes:
            if amps <= size:
                return size
        return 400

    @staticmethod
    def _get_feeder_wire(amps: int) -> str:
        """Get feeder wire size based on ampacity."""
        if amps <= 20:
            return "3.5mm²"
        elif amps <= 30:
            return "5.5mm²"
        elif amps <= 40:
            return "8mm²"
        elif amps <= 60:
            return "14mm²"
        elif amps <= 80:
            return "22mm²"
        elif amps <= 100:
            return "30mm²"
        elif amps <= 125:
            return "38mm²"
        elif amps <= 150:
            return "50mm²"
        else:
            return "60mm²"