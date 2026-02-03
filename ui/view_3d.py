from PySide6.QtDataVisualization import (Q3DBars, QBar3DSeries, QBarDataItem,
                                         QAbstract3DSeries, Q3DCamera)
from PySide6.QtGui import QColor, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout


class View3D(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # 1. Initialize 3D Graph
        self.chart = Q3DBars()
        self.container = QWidget.createWindowContainer(self.chart)
        layout.addWidget(self.container)

        # 2. Theme & Visuals - Dark Engineering Aesthetic
        theme = self.chart.activeTheme()
        theme.setBackgroundEnabled(True)
        theme.setBackgroundColor(QColor("#0d0f14"))
        theme.setLabelTextColor(QColor("#00e5ff"))
        theme.setGridEnabled(True)

        # Configure Axes for Spatial Mapping
        self.chart.valueAxis().setRange(0, 5000)
        self.chart.valueAxis().setTitle("Power Intensity (VA)")
        self.chart.valueAxis().setLabelFormat("%.0f VA")

        self.chart.rowAxis().setTitle("Floor Depth (Y)")
        self.chart.columnAxis().setTitle("Floor Width (X)")

        # 3. Series Setup with Thermal Gradient
        self.series = QBar3DSeries()

        try:
            self.series.setMesh(QAbstract3DSeries.MeshBevelBar)
        except AttributeError:
            self.series.setMesh(QAbstract3DSeries.MeshBox)

        gradient = QLinearGradient()
        gradient.setColorAt(0.0, QColor("#00e5ff"))  # Normal Load
        gradient.setColorAt(0.5, QColor("#f1c40f"))  # Moderate Load
        gradient.setColorAt(1.0, QColor("#ff4757"))  # Critical Load/AC
        self.series.setBaseGradient(gradient)

        if hasattr(QAbstract3DSeries, 'ColorStyleRangeGradient'):
            self.series.setColorStyle(QAbstract3DSeries.ColorStyleRangeGradient)

        self.chart.addSeries(self.series)

        # 4. FIXED CAMERA SETUP
        self.apply_camera_preset()

    def apply_camera_preset(self):
        """Safely applies camera presets by checking multiple naming conventions."""
        camera = self.chart.scene().activeCamera()

        # Possible locations for the enum value
        search_locations = [Q3DCamera.CameraPreset, Q3DCamera]
        preset_name = "IsometricRightHigh"

        applied = False
        for location in search_locations:
            if hasattr(location, preset_name):
                camera.setCameraPreset(getattr(location, preset_name))
                applied = True
                break

        # Fallback if Isometric isn't available
        if not applied:
            try:
                camera.setCameraPreset(Q3DCamera.CameraPreset.FrontHigh)
            except AttributeError:
                pass

    def update_3d_scene(self, electrical_items):
        """Maps canvas items to 3D space based on coordinates and VA."""
        if not electrical_items:
            self.series.dataProxy().resetArray([])
            return

        grid_resolution = 50
        load_map = {}

        for item in electrical_items:
            # Safely handle position data
            pos = item.pos()
            grid_x = str(int(pos.x() / grid_resolution))
            grid_y = str(int(pos.y() / grid_resolution))

            key = (grid_y, grid_x)
            load_map[key] = load_map.get(key, 0) + item.va

        # Sort keys to ensure the grid renders correctly
        sorted_keys = sorted(load_map.keys(), key=lambda x: (int(x[0]), int(x[1])))

        rows = sorted(list(set(k[0] for k in load_map.keys())), key=int)
        cols = sorted(list(set(k[1] for k in load_map.keys())), key=int)

        # FIXED: PySide6 uses setLabels instead of setCategories for QCategory3DAxis
        self.chart.rowAxis().setLabels(rows)
        self.chart.columnAxis().setLabels(cols)

        data_rows = []
        for r in rows:
            new_row = []
            for c in cols:
                va_value = load_map.get((r, c), 0)
                new_row.append(QBarDataItem(float(va_value)))
            data_rows.append(new_row)

        self.series.dataProxy().resetArray(data_rows)