"""
view_3d.py – AutoCAD-Style 3D Electrical Layout Viewer
========================================================
Professional isometric 3D visualization with:
  • Multiple view presets (Top, Front, Right, SW/SE/NW/NE Iso)
  • Wireframe / Shaded / Realistic render modes
  • Actual component extrusion as 3D boxes
  • Precision grid with axis tripod
  • Orbit / Zoom / Pan navigation
  • Component labels and wire routing paths
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QComboBox, QFrame, QButtonGroup, QToolButton,
    QSizePolicy, QGraphicsView, QGraphicsScene
)
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QTransform, QLinearGradient,
    QRadialGradient, QPainterPath, QPolygonF
)
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer, Signal, QEasingCurve, QPropertyAnimation

import math

# ==========================================================================
# COLOUR PALETTE  –  AutoCAD dark theme
# ==========================================================================
CLR_BG = QColor("#0d0f14")  # canvas background
CLR_GRID_MAJOR = QColor("#2d3646")  # major grid lines
CLR_GRID_MINOR = QColor("#1a1f26")  # minor grid lines
CLR_AXIS_X = QColor("#ff4757")  # X-axis red
CLR_AXIS_Y = QColor("#00ff88")  # Y-axis green
CLR_AXIS_Z = QColor("#00e5ff")  # Z-axis cyan
CLR_TEXT = QColor("#a0a0a0")  # dimension text
CLR_COMPONENT = QColor("#00e5ff")  # default component
CLR_HIGHLIGHT = QColor("#f1c40f")  # selected / hover
CLR_WIRE = QColor("#ff6b81")  # circuit wire


# ==========================================================================
# 3D MATH UTILITIES
# ==========================================================================
class IsoProjection:
    """Isometric projection matrix for 3D → 2D conversion.

    Standard isometric angles:
        - X-axis: 30° right-down
        - Y-axis: 30° left-down
        - Z-axis: vertical up
    """

    def __init__(self, scale: float = 1.0, rotation: float = 0.0, tilt: float = 30.0) -> None:
        self.scale = scale  # zoom factor
        self.rotation = rotation  # rotation around Z-axis (degrees)
        self.tilt = tilt  # vertical tilt (degrees)

    def project(self, x: float, y: float, z: float) -> QPointF:
        """Convert 3D world coordinates to 2D screen coordinates."""
        # Apply rotation
        rad = math.radians(self.rotation)
        xr = x * math.cos(rad) - y * math.sin(rad)
        yr = x * math.sin(rad) + y * math.cos(rad)

        # Isometric projection with tilt
        tilt_rad = math.radians(self.tilt)
        iso_x = (xr - yr) * math.cos(tilt_rad)
        iso_y = (xr + yr) * 0.5 * math.cos(tilt_rad) - z * math.sin(tilt_rad)

        return QPointF(iso_x * self.scale, iso_y * self.scale)


# ==========================================================================
# 3D SCENE  –  renders components as extruded 3D boxes
# ==========================================================================
class AutoCAD3DScene(QGraphicsScene):
    """Custom scene that renders electrical components in isometric 3D."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(CLR_BG))

        # Projection & camera
        self.projection = IsoProjection(scale=1.5, rotation=45, tilt=30)
        self.pan_offset = QPointF(0, 0)

        # Data
        self.components: list[dict] = []  # {name, x, y, z, va, w, h, d}
        self.wires: list[tuple] = []  # [(x1,y1,z1, x2,y2,z2), ...]
        self.render_mode = "shaded"  # wireframe | shaded | realistic
        self.show_grid = True
        self.show_labels = True
        self.show_axes = True

        # Grid bounds (auto-computed from components)
        self.grid_x_min = -500
        self.grid_x_max = 2500
        self.grid_y_min = -500
        self.grid_y_max = 2500
        self.grid_spacing = 100

    # ══════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════════
    def set_components(self, items: list) -> None:
        """Update the component list and trigger a redraw."""
        self.components.clear()

        for item in items:
            pos = item.pos()
            # Extrude height based on VA (taller = higher load)
            height = 20 + (item.va / 50.0)
            height = min(height, 200)  # cap at 200 px

            self.components.append({
                "name": item.name,
                "x": pos.x(),
                "y": pos.y(),
                "z": 0,  # all on ground plane for now
                "va": item.va,
                "w": 40,  # width
                "h": height,  # height (extrusion)
                "d": 40,  # depth
            })

        # Recompute grid bounds
        if self.components:
            xs = [c["x"] for c in self.components]
            ys = [c["y"] for c in self.components]
            self.grid_x_min = min(xs) - 200
            self.grid_x_max = max(xs) + 200
            self.grid_y_min = min(ys) - 200
            self.grid_y_max = max(ys) + 200

        self.redraw()

    def set_view_preset(self, preset: str) -> None:
        """Apply AutoCAD-style view presets."""
        presets = {
            "Top": {"rotation": 0, "tilt": 0},
            "Front": {"rotation": 0, "tilt": 90},
            "Right": {"rotation": 90, "tilt": 90},
            "SW_Iso": {"rotation": 45, "tilt": 30},
            "SE_Iso": {"rotation": 315, "tilt": 30},
            "NW_Iso": {"rotation": 135, "tilt": 30},
            "NE_Iso": {"rotation": 225, "tilt": 30},
        }

        if preset in presets:
            self.projection.rotation = presets[preset]["rotation"]
            self.projection.tilt = presets[preset]["tilt"]
            self.redraw()

    def set_render_mode(self, mode: str) -> None:
        """Switch between wireframe / shaded / realistic."""
        self.render_mode = mode
        self.redraw()

    def zoom(self, factor: float) -> None:
        """Adjust zoom level."""
        self.projection.scale *= factor
        self.projection.scale = max(0.2, min(self.projection.scale, 5.0))
        self.redraw()

    def pan(self, dx: float, dy: float) -> None:
        """Pan the view."""
        self.pan_offset += QPointF(dx, dy)
        self.redraw()

    def redraw(self) -> None:
        """Full scene rebuild."""
        self.clear()

        # 1. Draw grid plane
        if self.show_grid:
            self._draw_grid()

        # 2. Draw axis tripod
        if self.show_axes:
            self._draw_axes()

        # 3. Draw components (sorted back-to-front for proper occlusion)
        self._draw_components()

        # 4. Draw wires / circuit paths
        self._draw_wires()

        # Update scene rect to fit everything
        self.setSceneRect(self.itemsBoundingRect().adjusted(-100, -100, 100, 100))

    # ══════════════════════════════════════════════════════════════════
    # INTERNAL RENDERING
    # ══════════════════════════════════════════════════════════════════
    def _to_screen(self, x: float, y: float, z: float) -> QPointF:
        """World coords → screen coords (with pan offset)."""
        pt = self.projection.project(x, y, z)
        return pt + self.pan_offset

    def _draw_grid(self) -> None:
        """Render the ground plane grid."""
        pen_major = QPen(CLR_GRID_MAJOR, 1, Qt.SolidLine)
        pen_minor = QPen(CLR_GRID_MINOR, 1, Qt.DotLine)

        # Horizontal grid lines (along X)
        y = self.grid_y_min
        while y <= self.grid_y_max:
            p1 = self._to_screen(self.grid_x_min, y, 0)
            p2 = self._to_screen(self.grid_x_max, y, 0)
            pen = pen_major if y % (self.grid_spacing * 5) == 0 else pen_minor
            self.addLine(p1.x(), p1.y(), p2.x(), p2.y(), pen)
            y += self.grid_spacing

        # Vertical grid lines (along Y)
        x = self.grid_x_min
        while x <= self.grid_x_max:
            p1 = self._to_screen(x, self.grid_y_min, 0)
            p2 = self._to_screen(x, self.grid_y_max, 0)
            pen = pen_major if x % (self.grid_spacing * 5) == 0 else pen_minor
            self.addLine(p1.x(), p1.y(), p2.x(), p2.y(), pen)
            x += self.grid_spacing

    def _draw_axes(self) -> None:
        """Draw XYZ axis tripod at the origin."""
        origin = self._to_screen(0, 0, 0)
        axis_len = 150

        # X-axis (red)
        x_end = self._to_screen(axis_len, 0, 0)
        self.addLine(origin.x(), origin.y(), x_end.x(), x_end.y(), QPen(CLR_AXIS_X, 3))
        lbl_x = self.addText("X", QFont("Arial", 10, QFont.Bold))
        lbl_x.setDefaultTextColor(CLR_AXIS_X)
        lbl_x.setPos(x_end + QPointF(10, -10))

        # Y-axis (green)
        y_end = self._to_screen(0, axis_len, 0)
        self.addLine(origin.x(), origin.y(), y_end.x(), y_end.y(), QPen(CLR_AXIS_Y, 3))
        lbl_y = self.addText("Y", QFont("Arial", 10, QFont.Bold))
        lbl_y.setDefaultTextColor(CLR_AXIS_Y)
        lbl_y.setPos(y_end + QPointF(10, -10))

        # Z-axis (cyan)
        z_end = self._to_screen(0, 0, axis_len)
        self.addLine(origin.x(), origin.y(), z_end.x(), z_end.y(), QPen(CLR_AXIS_Z, 3))
        lbl_z = self.addText("Z", QFont("Arial", 10, QFont.Bold))
        lbl_z.setDefaultTextColor(CLR_AXIS_Z)
        lbl_z.setPos(z_end + QPointF(10, -10))

    def _draw_components(self) -> None:
        """Render each component as a 3D extruded box."""
        # Sort components back-to-front for painter's algorithm
        # (simple depth = x + y + z; more sophisticated would use proper Z-buffer)
        sorted_comps = sorted(self.components, key=lambda c: c["x"] + c["y"] + c["z"])

        for comp in sorted_comps:
            self._draw_box(
                comp["x"], comp["y"], comp["z"],
                comp["w"], comp["h"], comp["d"],
                comp["name"], comp["va"]
            )

    def _draw_box(self, x: float, y: float, z: float,
                  w: float, h: float, d: float,
                  name: str, va: float) -> None:
        """Draw a single 3D box (component) in isometric view.

        Box corners:
            Bottom face (z):      Top face (z+h):
            0 ---- 1              4 ---- 5
            |      |              |      |
            3 ---- 2              7 ---- 6
        """
        # Define 8 vertices
        v0 = self._to_screen(x, y, z)
        v1 = self._to_screen(x + w, y, z)
        v2 = self._to_screen(x + w, y + d, z)
        v3 = self._to_screen(x, y + d, z)
        v4 = self._to_screen(x, y, z + h)
        v5 = self._to_screen(x + w, y, z + h)
        v6 = self._to_screen(x + w, y + d, z + h)
        v7 = self._to_screen(x, y + d, z + h)

        # ── Determine fill color based on VA (thermal gradient) ──
        if va < 500:
            base_color = QColor("#00e5ff")  # low load – cyan
        elif va < 2000:
            base_color = QColor("#f1c40f")  # medium – yellow
        else:
            base_color = QColor("#ff4757")  # high load – red

        # ══════════════════════════════════════════════════════════════
        # RENDER MODE DISPATCH
        # ══════════════════════════════════════════════════════════════
        if self.render_mode == "wireframe":
            self._draw_box_wireframe(v0, v1, v2, v3, v4, v5, v6, v7, base_color)
        elif self.render_mode == "shaded":
            self._draw_box_shaded(v0, v1, v2, v3, v4, v5, v6, v7, base_color)
        else:  # realistic
            self._draw_box_realistic(v0, v1, v2, v3, v4, v5, v6, v7, base_color)

        # ── Component label ───────────────────────────────────────────
        if self.show_labels:
            # Place label above the top face
            label_pos = (v4 + v5 + v6 + v7) / 4.0 + QPointF(0, -15)
            lbl = self.addText(f"{name}\n{va} VA", QFont("Consolas", 8))
            lbl.setDefaultTextColor(CLR_TEXT)
            lbl.setPos(label_pos - QPointF(lbl.boundingRect().width() / 2, 0))

    # ── Wireframe mode ────────────────────────────────────────────────
    def _draw_box_wireframe(self, v0, v1, v2, v3, v4, v5, v6, v7, color: QColor) -> None:
        pen = QPen(color, 2)
        # Bottom face
        self.addLine(v0.x(), v0.y(), v1.x(), v1.y(), pen)
        self.addLine(v1.x(), v1.y(), v2.x(), v2.y(), pen)
        self.addLine(v2.x(), v2.y(), v3.x(), v3.y(), pen)
        self.addLine(v3.x(), v3.y(), v0.x(), v0.y(), pen)
        # Top face
        self.addLine(v4.x(), v4.y(), v5.x(), v5.y(), pen)
        self.addLine(v5.x(), v5.y(), v6.x(), v6.y(), pen)
        self.addLine(v6.x(), v6.y(), v7.x(), v7.y(), pen)
        self.addLine(v7.x(), v7.y(), v4.x(), v4.y(), pen)
        # Vertical edges
        self.addLine(v0.x(), v0.y(), v4.x(), v4.y(), pen)
        self.addLine(v1.x(), v1.y(), v5.x(), v5.y(), pen)
        self.addLine(v2.x(), v2.y(), v6.x(), v6.y(), pen)
        self.addLine(v3.x(), v3.y(), v7.x(), v7.y(), pen)

    # ── Shaded mode (flat faces with simple lighting) ────────────────
    def _draw_box_shaded(self, v0, v1, v2, v3, v4, v5, v6, v7, color: QColor) -> None:
        """Draw three visible faces with flat shading."""
        # Determine which faces are visible based on normal vectors
        # (simplified: assume camera is always above and to the right)

        # Top face (always visible if box has height)
        top_color = color.lighter(130)
        top_poly = QPolygonF([v4, v5, v6, v7])
        self.addPolygon(top_poly, QPen(color.darker(120), 1), QBrush(top_color))

        # Right face (x+w side)
        right_color = color.darker(110)
        right_poly = QPolygonF([v1, v2, v6, v5])
        self.addPolygon(right_poly, QPen(color.darker(150), 1), QBrush(right_color))

        # Front face (y+d side)
        front_color = color.darker(120)
        front_poly = QPolygonF([v2, v3, v7, v6])
        self.addPolygon(front_poly, QPen(color.darker(150), 1), QBrush(front_color))

    # ── Realistic mode (gradient lighting) ───────────────────────────
    def _draw_box_realistic(self, v0, v1, v2, v3, v4, v5, v6, v7, color: QColor) -> None:
        """Draw faces with radial gradients for depth."""
        # Top face – radial gradient from centre
        top_centre = (v4 + v5 + v6 + v7) / 4.0
        top_grad = QRadialGradient(top_centre, 50)
        top_grad.setColorAt(0.0, color.lighter(140))
        top_grad.setColorAt(1.0, color)
        top_poly = QPolygonF([v4, v5, v6, v7])
        self.addPolygon(top_poly, QPen(color.darker(120), 1), QBrush(top_grad))

        # Right face
        right_centre = (v1 + v2 + v6 + v5) / 4.0
        right_grad = QRadialGradient(right_centre, 40)
        right_grad.setColorAt(0.0, color.darker(100))
        right_grad.setColorAt(1.0, color.darker(130))
        right_poly = QPolygonF([v1, v2, v6, v5])
        self.addPolygon(right_poly, QPen(color.darker(150), 1), QBrush(right_grad))

        # Front face
        front_centre = (v2 + v3 + v7 + v6) / 4.0
        front_grad = QRadialGradient(front_centre, 40)
        front_grad.setColorAt(0.0, color.darker(110))
        front_grad.setColorAt(1.0, color.darker(140))
        front_poly = QPolygonF([v2, v3, v7, v6])
        self.addPolygon(front_poly, QPen(color.darker(150), 1), QBrush(front_grad))

    def _draw_wires(self) -> None:
        """Render circuit wire paths as 3D lines."""
        pen = QPen(CLR_WIRE, 2, Qt.DashLine)
        for (x1, y1, z1, x2, y2, z2) in self.wires:
            p1 = self._to_screen(x1, y1, z1)
            p2 = self._to_screen(x2, y2, z2)
            self.addLine(p1.x(), p1.y(), p2.x(), p2.y(), pen)


# ==========================================================================
# AUTOCAD-STYLE 3D VIEW WIDGET
# ==========================================================================
class View3D(QWidget):
    """Main widget with toolbar + 3D viewport."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # ── Main layout ───────────────────────────────────────────────
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Toolbar (top) ─────────────────────────────────────────────
        toolbar = self._build_toolbar()
        main_layout.addWidget(toolbar)

        # ── 3D Viewport ───────────────────────────────────────────────
        self.scene = AutoCAD3DScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("border: none; background: #0d0f14;")

        main_layout.addWidget(self.view, stretch=1)

        # ── Status bar (bottom) ───────────────────────────────────────
        status = self._build_status_bar()
        main_layout.addWidget(status)

        # Mouse interaction state
        self._last_mouse_pos = None

    # ══════════════════════════════════════════════════════════════════
    # UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════════════
    def _build_toolbar(self) -> QFrame:
        """Top toolbar with view controls."""
        frame = QFrame()
        frame.setFixedHeight(44)
        frame.setStyleSheet("""
            QFrame {
                background-color: #1a1f26;
                border-bottom: 1px solid #2d3646;
            }
            QPushButton, QToolButton {
                background-color: #1c222d;
                color: #00e5ff;
                border: 1px solid #2d3646;
                border-radius: 3px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #252e3e;
                border-color: #00e5ff;
            }
            QPushButton:checked, QToolButton:checked {
                background-color: #00e5ff;
                color: #0d0f14;
            }
            QComboBox {
                background-color: #1c222d;
                color: #fff;
                border: 1px solid #2d3646;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QLabel {
                color: #a0a0a0;
                font-size: 10px;
                font-weight: bold;
            }
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # ── View preset buttons ───────────────────────────────────────
        layout.addWidget(QLabel("VIEW:"))

        view_group = QButtonGroup(self)
        view_group.setExclusive(True)

        for label, preset in [
            ("⬆ Top", "Top"),
            ("◧ Front", "Front"),
            ("◨ Right", "Right"),
            ("⬉ SW Iso", "SW_Iso"),
            ("⬈ SE Iso", "SE_Iso"),
            ("⬊ NW Iso", "NW_Iso"),
            ("⬋ NE Iso", "NE_Iso"),
        ]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _c, p=preset: self.scene.set_view_preset(p))
            view_group.addButton(btn)
            layout.addWidget(btn)
            if preset == "SW_Iso":  # default
                btn.setChecked(True)

        layout.addSpacing(12)

        # ── Render mode selector ──────────────────────────────────────
        layout.addWidget(QLabel("RENDER:"))

        self.render_combo = QComboBox()
        self.render_combo.addItems(["Wireframe", "Shaded", "Realistic"])
        self.render_combo.setCurrentText("Shaded")
        self.render_combo.currentTextChanged.connect(
            lambda txt: self.scene.set_render_mode(txt.lower())
        )
        layout.addWidget(self.render_combo)

        layout.addSpacing(12)

        # ── Toggle switches ───────────────────────────────────────────
        self.btn_grid = QPushButton("◫ Grid")
        self.btn_grid.setCheckable(True)
        self.btn_grid.setChecked(True)
        self.btn_grid.clicked.connect(lambda c: self._toggle_grid(c))
        layout.addWidget(self.btn_grid)

        self.btn_axes = QPushButton("⊹ Axes")
        self.btn_axes.setCheckable(True)
        self.btn_axes.setChecked(True)
        self.btn_axes.clicked.connect(lambda c: self._toggle_axes(c))
        layout.addWidget(self.btn_axes)

        self.btn_labels = QPushButton("🏷 Labels")
        self.btn_labels.setCheckable(True)
        self.btn_labels.setChecked(True)
        self.btn_labels.clicked.connect(lambda c: self._toggle_labels(c))
        layout.addWidget(self.btn_labels)

        layout.addStretch()

        # ── Zoom controls ─────────────────────────────────────────────
        layout.addWidget(QLabel("ZOOM:"))

        btn_zoom_in = QPushButton("🔍 +")
        btn_zoom_in.clicked.connect(lambda: self.scene.zoom(1.2))
        layout.addWidget(btn_zoom_in)

        btn_zoom_out = QPushButton("🔍 −")
        btn_zoom_out.clicked.connect(lambda: self.scene.zoom(0.8))
        layout.addWidget(btn_zoom_out)

        btn_fit = QPushButton("⛶ Fit")
        btn_fit.clicked.connect(self._fit_to_view)
        layout.addWidget(btn_fit)

        return frame

    def _build_status_bar(self) -> QFrame:
        """Bottom status bar showing stats."""
        frame = QFrame()
        frame.setFixedHeight(28)
        frame.setStyleSheet("""
            QFrame {
                background-color: #12151b;
                border-top: 1px solid #2d3646;
            }
            QLabel {
                color: #a0a0a0;
                font-size: 10px;
                padding: 0 8px;
            }
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(4, 0, 4, 0)

        self.lbl_status = QLabel("Ready  │  Components: 0  │  View: SW Isometric")
        layout.addWidget(self.lbl_status)
        layout.addStretch()

        return frame

    # ══════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════════════
    def update_3d_scene(self, electrical_items: list) -> None:
        """Main entry point called by the app when the 3D tab is opened."""
        self.scene.set_components(electrical_items)
        self._fit_to_view()

        # Update status bar
        self.lbl_status.setText(
            f"Ready  │  Components: {len(electrical_items)}  │  "
            f"View: {self.render_combo.currentText()}"
        )

    # ══════════════════════════════════════════════════════════════════
    # INTERNAL HELPERS
    # ══════════════════════════════════════════════════════════════════
    def _toggle_grid(self, checked: bool) -> None:
        self.scene.show_grid = checked
        self.scene.redraw()

    def _toggle_axes(self, checked: bool) -> None:
        self.scene.show_axes = checked
        self.scene.redraw()

    def _toggle_labels(self, checked: bool) -> None:
        self.scene.show_labels = checked
        self.scene.redraw()

    def _fit_to_view(self) -> None:
        """Reset zoom/pan to fit all components."""
        self.scene.projection.scale = 1.5
        self.scene.pan_offset = QPointF(400, 300)  # reasonable default centre
        self.scene.redraw()
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    # ══════════════════════════════════════════════════════════════════
    # MOUSE INTERACTION  (orbit + pan)
    # ══════════════════════════════════════════════════════════════════
    def wheelEvent(self, event) -> None:
        """Mouse wheel = zoom."""
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else 0.9
        self.scene.zoom(factor)

    # For advanced orbit controls you'd override mousePressEvent / mouseMoveEvent
    # and adjust self.scene.projection.rotation based on drag delta.
    # Keeping it simple here with ScrollHandDrag for pan only.