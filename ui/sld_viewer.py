import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene,
                               QPushButton, QHBoxLayout, QFileDialog, QMessageBox)
from PySide6.QtGui import QPainter, QPen, QFont, QColor, QBrush, QImage
from PySide6.QtCore import Qt, QRectF


class SLDViewer(QDialog):
    def __init__(self, electrical_data):
        super().__init__()
        self.setWindowTitle("ELECDRAFT - Auto-Generated Single Line Diagram")
        self.resize(1100, 850)

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Scene & View Setup
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor("#0d0f14"))

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.TextAntialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)

        self.main_layout.addWidget(self.view)

        # 2. Bottom Action Bar
        self.controls = QHBoxLayout()
        self.controls.setContentsMargins(10, 10, 10, 10)

        self.btn_export = QPushButton("📸 SAVE AS IMAGE (PNG)")
        self.btn_export.setFixedHeight(40)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #00b894;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #55efc4; }
        """)
        self.btn_export.clicked.connect(self.export_image)

        self.controls.addStretch()
        self.controls.addWidget(self.btn_export)
        self.main_layout.addLayout(self.controls)

        # 3. Generate Schematic
        self.generate_diagram(electrical_data)

    def draw_load_symbol(self, x, y, item_name, pen):
        name_lower = item_name.lower()
        if "light" in name_lower:
            self.scene.addEllipse(x - 20, y, 40, 40, pen)
            self.scene.addLine(x - 14, y + 6, x + 14, y + 34, pen)
            self.scene.addLine(x + 14, y + 6, x - 14, y + 34, pen)
        elif "duplex" in name_lower or "plug" in name_lower:
            self.scene.addEllipse(x - 20, y, 40, 40, pen)
            self.scene.addLine(x - 25, y + 15, x + 25, y + 15, pen)
            self.scene.addLine(x - 25, y + 25, x + 25, y + 25, pen)
        else:
            self.scene.addEllipse(x - 20, y, 40, 40, pen)
            m_txt = self.scene.addText("M", QFont("Segoe UI", 12, QFont.Weight.Bold))
            m_txt.setDefaultTextColor(Qt.white)
            m_txt.setPos(x - 11, y + 4)

    def generate_diagram(self, data):
        pen = QPen(QColor("#d2dae2"), 2)
        bus_pen = QPen(QColor("#00e5ff"), 6)
        font_bold = QFont("Segoe UI", 10, QFont.Weight.Bold)
        font_small = QFont("Consolas", 8)
        accent_color = QColor("#00e5ff")

        # Main Entrance
        self.scene.addLine(500, -150, 500, -50, pen)
        srv_txt = "SERVICE ENTRANCE\n230V, 1-PHASE, 2-WIRE\n60 Hz, AC SYSTEM"
        source_lbl = self.scene.addText(srv_txt, font_bold)
        source_lbl.setDefaultTextColor(accent_color)
        source_lbl.setPos(520, -140)

        main_brk = self.scene.addRect(480, -50, 40, 60, pen)
        main_brk.setBrush(QBrush(QColor("#1e272e")))

        # Busbar
        spacing = 220
        bus_width = max(600, len(data) * spacing)
        start_x = 500 - (bus_width / 2)
        self.scene.addLine(start_x, 80, start_x + bus_width, 80, bus_pen)

        # Branch Circuits
        for i, item in enumerate(data):
            x_pos = (start_x + (spacing / 2)) + (i * spacing)
            self.scene.addLine(x_pos, 80, x_pos, 140, pen)
            brk = self.scene.addRect(x_pos - 15, 140, 30, 50, pen)
            brk.setBrush(QBrush(QColor("#2f3640")))
            self.scene.addLine(x_pos, 190, x_pos, 260, pen)
            self.draw_load_symbol(x_pos, 260, item['name'], pen)

            specs = (f"CKT NO. {i + 1}\nLOAD: {item['name'].upper()}\n"
                     f"PROT: {item['breaker']}AT, 2P\nWIRE: {item['wire']}\n"
                     f"CONDUIT: 20mmØ IMC")
            txt = self.scene.addText(specs, font_small)
            txt.setDefaultTextColor(QColor("#adb5bd"))
            txt.setPos(x_pos + 25, 145)

        self.view.fitInView(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100),
                            Qt.AspectRatioMode.KeepAspectRatio)

    def export_image(self):
        """Captures the scene and saves it as a high-res PNG."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Schematic", "SLD_Diagram.png", "PNG Files (*.png)")
        if not file_path:
            return

        # Define resolution (2x for high quality)
        rect = self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50)
        image = QImage(rect.size().toSize() * 2, QImage.Format_ARGB32)
        image.fill(QColor("#0d0f14"))  # Match background

        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        self.scene.render(painter, QRectF(image.rect()), rect)
        painter.end()

        if image.save(file_path):
            QMessageBox.information(self, "Export Success", f"Diagram saved to:\n{file_path}")

    def resizeEvent(self, event):
        if not self.scene.itemsBoundingRect().isEmpty():
            self.view.fitInView(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100),
                                Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)