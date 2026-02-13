"""
sld_viewer.py – Professional SLD Viewer Dialog
===============================================
Displays generated single-line diagrams with export and zoom controls.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QFileDialog, QMessageBox,
    QFrame, QSlider, QComboBox
)
from PySide6.QtGui import (
    QPainter, QPixmap, QPen, QColor, QFont, QImage
)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtPrintSupport import QPrinter

from modules.sld_generator import SLDGenerator


# ==========================================================================
# SLD VIEWER DIALOG
# ==========================================================================
class SLDViewer(QDialog):
    """Professional dialog for viewing and exporting single-line diagrams."""

    def __init__(self, sld_data: list, project_data: dict = None, parent=None) -> None:
        super().__init__(parent)

        self.sld_data = sld_data
        self.project_data = project_data or {
            "name": "Main Panel",
            "system_voltage": 230,
            "standard": "PEC 2017"
        }

        # ── Window setup ──────────────────────────────────────────────
        self.setWindowTitle("Single Line Diagram Viewer – ELECDRAFT PRO")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)

        # ── Build UI ──────────────────────────────────────────────────
        self._setup_ui()

        # ── Generate diagram ──────────────────────────────────────────
        self._render_diagram()

        # ── Apply styles ──────────────────────────────────────────────
        self._apply_styles()

    # ══════════════════════════════════════════════════════════════════
    # UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════════════
    def _setup_ui(self) -> None:
        """Build the dialog layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = self._build_toolbar()
        main_layout.addWidget(toolbar)

        # ── Graphics view ─────────────────────────────────────────────
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        main_layout.addWidget(self.view, stretch=1)

        # ── Status bar ────────────────────────────────────────────────
        status = self._build_status_bar()
        main_layout.addWidget(status)

    def _build_toolbar(self) -> QFrame:
        """Top toolbar with controls."""
        frame = QFrame()
        frame.setFixedHeight(50)
        frame.setObjectName("toolbar")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Title
        title = QLabel("📉 SINGLE LINE DIAGRAM")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(title)

        layout.addStretch()

        # Zoom controls
        layout.addWidget(QLabel("Zoom:"))

        btn_zoom_in = QPushButton("🔍 +")
        btn_zoom_in.clicked.connect(lambda: self.view.scale(1.2, 1.2))
        layout.addWidget(btn_zoom_in)

        btn_zoom_out = QPushButton("🔍 −")
        btn_zoom_out.clicked.connect(lambda: self.view.scale(0.8, 0.8))
        layout.addWidget(btn_zoom_out)

        btn_fit = QPushButton("⛶ Fit")
        btn_fit.clicked.connect(lambda: self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio))
        layout.addWidget(btn_fit)

        layout.addSpacing(12)

        # Export buttons
        btn_export_pdf = QPushButton("🖨️ Export PDF")
        btn_export_pdf.clicked.connect(self._export_pdf)
        layout.addWidget(btn_export_pdf)

        btn_export_png = QPushButton("🖼️ Export PNG")
        btn_export_png.clicked.connect(self._export_png)
        layout.addWidget(btn_export_png)

        layout.addSpacing(12)

        # Close button
        btn_close = QPushButton("✖ Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

        return frame

    def _build_status_bar(self) -> QFrame:
        """Bottom status bar."""
        frame = QFrame()
        frame.setFixedHeight(32)
        frame.setObjectName("statusbar")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 0, 12, 0)

        self.lbl_status = QLabel(f"Circuits: {len(self.sld_data)}  │  Ready")
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        lbl_tip = QLabel("💡 Click and drag to pan  │  Use toolbar to zoom")
        lbl_tip.setStyleSheet("color: #636C76; font-size: 9px;")
        layout.addWidget(lbl_tip)

        return frame

    # ══════════════════════════════════════════════════════════════════
    # DIAGRAM RENDERING
    # ══════════════════════════════════════════════════════════════════
    def _render_diagram(self) -> None:
        """Generate the SLD and add to scene."""
        # Calculate canvas size
        circuit_count = len(self.sld_data)
        width = 800
        height = 200 + circuit_count * 70 + 200  # header + circuits + footer

        # Create pixmap
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.white)

        # Draw diagram
        painter = QPainter(pixmap)
        SLDGenerator.draw_diagram(painter, self.sld_data, self.project_data)
        painter.end()

        # Add to scene
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(0, 0, width, height)

        # Fit to view
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    # ══════════════════════════════════════════════════════════════════
    # EXPORT FUNCTIONS
    # ══════════════════════════════════════════════════════════════════
    def _export_pdf(self) -> None:
        """Export diagram to PDF."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export SLD to PDF", "", "PDF Files (*.pdf)"
        )
        if not path:
            return

        try:
            # Create printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            printer.setPageOrientation(QPrinter.Portrait)
            printer.setPageSize(QPrinter.Letter)

            # Render scene to printer
            painter = QPainter(printer)
            self.scene.render(painter)
            painter.end()

            self.lbl_status.setText(f"✓ Exported to: {path}")
            QMessageBox.information(self, "Export Success", f"SLD exported to:\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{e}")

    def _export_png(self) -> None:
        """Export diagram to PNG."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export SLD to PNG", "", "PNG Files (*.png)"
        )
        if not path:
            return

        try:
            # Render scene to image
            rect = self.scene.sceneRect()
            image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
            image.fill(Qt.white)

            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter)
            painter.end()

            image.save(path, "PNG")

            self.lbl_status.setText(f"✓ Exported to: {path}")
            QMessageBox.information(self, "Export Success", f"SLD exported to:\n{path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export PNG:\n{e}")

    # ══════════════════════════════════════════════════════════════════
    # STYLING
    # ══════════════════════════════════════════════════════════════════
    def _apply_styles(self) -> None:
        """Apply professional dark theme."""
        self.setStyleSheet("""
            QDialog {
                background-color: #0E1013;
            }

            #toolbar {
                background-color: #1A1F26;
                border-bottom: 1px solid #2D3646;
            }

            #statusbar {
                background-color: #12151B;
                border-top: 1px solid #2D3646;
            }

            QLabel {
                color: #ECEFF4;
                font-size: 10px;
            }

            QPushButton {
                background-color: #1C222D;
                color: #00D9FF;
                border: 1px solid #2D3646;
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #252E3E;
                border-color: #00D9FF;
            }

            QPushButton:pressed {
                background-color: #1A2030;
            }

            QGraphicsView {
                background-color: #161A1F;
                border: 1px solid #2D3646;
                border-radius: 4px;
                margin: 8px;
            }
        """)