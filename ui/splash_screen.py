from PySide6.QtWidgets import QSplashScreen
from PySide6.QtCore import Qt, QTimer, QRect, QPointF
from PySide6.QtGui import (QPixmap, QPainter, QColor, QFont, QPen, QLinearGradient,
                           QRadialGradient, QBrush, QPainterPath)


class EnhancedSplash(QSplashScreen):
    """Premium professional splash screen with cached rendering and modern UI."""

    def __init__(self, logo_path, parent=None):
        self.width, self.height = 700, 450
        # Initialize the high-quality base
        self.base_pixmap = QPixmap(self.width, self.height)
        self.base_pixmap.fill(Qt.transparent)

        self.logo_path = logo_path
        self._generate_base_ui()

        super().__init__(self.base_pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SplashScreen)

        # Logic State
        self.current_progress = 0
        self.current_message = "Initializing Engine..."
        self.pulse_value = 0
        self.pulse_dir = 1

        # Timers
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._update_animation)
        self.pulse_timer.start(30)

        self.setWindowOpacity(0.0)
        QTimer.singleShot(10, self._fade_in)

    def _generate_base_ui(self):
        """Draws the static parts of the UI once to save CPU."""
        painter = QPainter(self.base_pixmap)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        # Background Path (Rounded)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, 12, 12)
        painter.setClipPath(path)

        # Dark Cinematic Gradient
        bg_grad = QLinearGradient(0, 0, 0, self.height)
        bg_grad.setColorAt(0, QColor("#0d1117"))
        bg_grad.setColorAt(1, QColor("#010409"))
        painter.fillPath(path, bg_grad)

        # Subtle Radial Glow from Top
        top_glow = QRadialGradient(self.width / 2, 0, self.height)
        top_glow.setColorAt(0, QColor(0, 229, 255, 15))
        top_glow.setColorAt(1, Qt.transparent)
        painter.fillPath(path, top_glow)

        # Logo Logic
        logo = QPixmap(self.logo_path)
        if not logo.isNull():
            logo_s = logo.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(int((self.width - 140) / 2), 50, logo_s)

        # Typography: Title
        painter.setPen(QColor("#f0f6fc"))
        painter.setFont(QFont("Segoe UI Variable Display", 26, QFont.Bold))
        painter.drawText(0, 240, self.width, 50, Qt.AlignCenter, "ELECDRAFT PRO")

        # Typography: Subtitle
        painter.setPen(QColor("#8b949e"))
        painter.setFont(QFont("Segoe UI Variable Text", 10, QFont.Light))
        painter.drawText(0, 275, self.width, 30, Qt.AlignCenter, "ADVANCED ELECTRICAL ENGINEERING CAD")

        # Refined Footer
        painter.setPen(QColor("#484f58"))
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(20, self.height - 20, "PEC 2017 | BUILT WITH PYSIDE6")
        painter.drawText(self.width - 150, self.height - 20, "© 2025 ELECDRAFT")

        # Hairline Border
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawRoundedRect(1, 1, self.width - 2, self.height - 2, 11, 11)
        painter.end()

    def _update_animation(self):
        self.pulse_value += 2 * self.pulse_dir
        if self.pulse_value >= 100 or self.pulse_value <= 0:
            self.pulse_dir *= -1
        self.update()

    def _fade_in(self):
        self.opacity_timer = QTimer(self)
        self.curr_opacity = 0.0

        def step():
            self.curr_opacity += 0.05
            self.setWindowOpacity(self.curr_opacity)
            if self.curr_opacity >= 1.0: self.opacity_timer.stop()

        self.opacity_timer.timeout.connect(step)
        self.opacity_timer.start(20)

    def showMessage(self, message, *args, **kwargs):
        self.current_message = message.upper()
        self.update()

    def set_progress(self, val):
        self.current_progress = val
        self.update()

    def drawContents(self, painter):
        """Only draw dynamic elements here for high performance."""
        painter.setRenderHint(QPainter.Antialiasing)

        # Progress Bar Config
        bx, by, bw, bh = 150, 340, 400, 4

        # Bar Background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.drawRoundedRect(bx, by, bw, bh, 2, 2)

        # Bar Fill
        fill_w = int(bw * (self.current_progress / 100))
        if fill_w > 0:
            # Glossy Fill
            fill_grad = QLinearGradient(bx, by, bx + fill_w, by)
            fill_grad.setColorAt(0, QColor("#0077b6"))
            fill_grad.setColorAt(1, QColor("#00e5ff"))

            painter.setBrush(fill_grad)
            painter.drawRoundedRect(bx, by, fill_w, bh, 2, 2)

            # Glow Effect
            glow_alpha = 50 + (self.pulse_value // 2)
            painter.setPen(QPen(QColor(0, 229, 255, glow_alpha), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(bx - 1, by - 1, fill_w + 2, bh + 2, 2, 2)

        # Status Message
        painter.setPen(QColor("#58a6ff"))
        painter.setFont(QFont("Segoe UI Semibold", 8))
        painter.drawText(bx, by + 25, self.current_message)

        # Loading Indicator (Spinning effect simulated with dots)
        dots = "." * (int(self.pulse_value / 25) % 4)
        painter.drawText(bx + painter.fontMetrics().horizontalAdvance(self.current_message) + 2, by + 25, dots)

    def finish_loading(self, main_win):
        self.pulse_timer.stop()
        self.set_progress(100)
        QTimer.singleShot(200, lambda: self.finish(main_win))