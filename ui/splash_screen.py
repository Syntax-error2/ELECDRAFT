"""
splash_screen.py – Professional & Elegant Enterprise Splash Screen
===================================================================
Inspired by AutoCAD, Revit, Adobe CC, and Figma.

Design Philosophy:
  • Restraint over excess
  • Precision over decoration
  • Clarity over complexity
  • Elegance through simplicity
"""

from PySide6.QtWidgets import QSplashScreen
from PySide6.QtCore import Qt, QTimer, QRect, QRectF, QPointF
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QFont, QPen, QLinearGradient,
    QRadialGradient, QBrush, QPainterPath
)
import math


# ==========================================================================
# PROFESSIONAL COLOR PALETTE
# ==========================================================================
class Colors:
    """Enterprise-grade color system with semantic naming."""

    # Backgrounds
    BG_DEEP = QColor("#090A0D")
    BG_PRIMARY = QColor("#0E1013")
    BG_ELEVATED = QColor("#161A1F")
    BG_CARD = QColor("#1A1F26")

    # Borders
    BORDER_SUBTLE = QColor("#21262D")
    BORDER_MEDIUM = QColor("#2D333B")
    BORDER_STRONG = QColor("#373E47")

    # Text
    TEXT_PRIMARY = QColor("#ECEFF4")
    TEXT_SECONDARY = QColor("#8B949E")
    TEXT_TERTIARY = QColor("#636C76")
    TEXT_DISABLED = QColor("#484F58")

    # Accents
    ACCENT_PRIMARY = QColor("#00D9FF")
    ACCENT_GLOW = QColor("#0099CC")
    ACCENT_SOFT = QColor("#00B4D8")


# ==========================================================================
# ELEGANT PARTICLE
# ==========================================================================
class ElegantParticle:
    """Minimal floating particle for subtle background motion."""

    def __init__(self, width: int, height: int) -> None:
        import random
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.vx = random.uniform(-0.15, 0.15)
        self.vy = random.uniform(-0.25, 0.1)
        self.size = random.uniform(1.0, 2.5)
        self.base_opacity = random.uniform(20, 60)
        self.phase = random.uniform(0, 2 * math.pi)
        self.bounds = (width, height)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.phase += 0.03

        if self.x < 0:
            self.x = self.bounds[0]
        elif self.x > self.bounds[0]:
            self.x = 0
        if self.y < 0:
            self.y = self.bounds[1]
        elif self.y > self.bounds[1]:
            self.y = 0

    def draw(self, painter: QPainter) -> None:
        opacity = self.base_opacity + 20 * math.sin(self.phase)

        glow = QRadialGradient(QPointF(self.x, self.y), self.size * 3)
        glow.setColorAt(0.0, QColor(0, 217, 255, int(opacity * 0.4)))
        glow.setColorAt(0.7, QColor(0, 217, 255, int(opacity * 0.1)))
        glow.setColorAt(1.0, Qt.transparent)

        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(self.x, self.y), self.size * 3, self.size * 3)

        painter.setBrush(QColor(0, 217, 255, int(opacity)))
        painter.drawEllipse(QPointF(self.x, self.y), self.size * 0.8, self.size * 0.8)


# ==========================================================================
# PROFESSIONAL SPLASH SCREEN
# ==========================================================================
class EnhancedSplash(QSplashScreen):
    """Enterprise-grade splash screen with elegant, minimal design."""

    def __init__(self, logo_path: str, parent=None) -> None:
        self.width = 720
        self.height = 480

        self.base_pixmap = QPixmap(self.width, self.height)
        self.base_pixmap.fill(Qt.transparent)

        self.logo_path = logo_path
        self._particles = [ElegantParticle(self.width, self.height) for _ in range(35)]

        self.current_progress = 0
        self.smooth_progress = 0.0
        self.current_message = "Initializing System..."
        self.pulse_value = 0.0
        self.logo_opacity = 0.0
        self.content_opacity = 0.0

        self._generate_base()

        super().__init__(self.base_pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SplashScreen)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update)
        self.anim_timer.start(16)

        self.setWindowOpacity(0.0)
        QTimer.singleShot(50, self._fade_in)

    def _generate_base(self) -> None:
        painter = QPainter(self.base_pixmap)
        painter.setRenderHints(
            QPainter.Antialiasing |
            QPainter.TextAntialiasing |
            QPainter.SmoothPixmapTransform
        )

        corner_radius = 8
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width, self.height), corner_radius, corner_radius)
        painter.setClipPath(path)

        bg_grad = QLinearGradient(0, 0, 0, self.height)
        bg_grad.setColorAt(0.0, Colors.BG_DEEP)
        bg_grad.setColorAt(0.3, Colors.BG_PRIMARY)
        bg_grad.setColorAt(1.0, Colors.BG_DEEP)
        painter.fillPath(path, bg_grad)

        accent_glow = QRadialGradient(self.width / 2, self.height * 0.25, self.height * 0.7)
        accent_glow.setColorAt(0.0, QColor(0, 217, 255, 12))
        accent_glow.setColorAt(0.5, QColor(0, 180, 210, 6))
        accent_glow.setColorAt(1.0, Qt.transparent)
        painter.fillPath(path, accent_glow)

        card_margin = 60
        card_rect = QRectF(card_margin, card_margin,
                           self.width - card_margin * 2,
                           self.height - card_margin * 2)

        card_path = QPainterPath()
        card_path.addRoundedRect(card_rect, 6, 6)

        card_grad = QLinearGradient(0, card_margin, 0, self.height - card_margin)
        card_grad.setColorAt(0.0, QColor(255, 255, 255, 4))
        card_grad.setColorAt(0.5, QColor(255, 255, 255, 2))
        card_grad.setColorAt(1.0, QColor(255, 255, 255, 4))
        painter.fillPath(card_path, card_grad)

        painter.setPen(QPen(Colors.BORDER_SUBTLE, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(card_rect, 6, 6)

        painter.setPen(QPen(Colors.BORDER_MEDIUM, 1.5))
        painter.drawRoundedRect(
            QRectF(0.75, 0.75, self.width - 1.5, self.height - 1.5),
            corner_radius, corner_radius
        )

        painter.end()

    def _update(self) -> None:
        self.pulse_value += 0.04

        diff = (self.current_progress / 100.0) - self.smooth_progress
        self.smooth_progress += diff * 0.12

        if self.logo_opacity < 1.0:
            self.logo_opacity += 0.015
        if self.content_opacity < 1.0:
            self.content_opacity += 0.02

        for p in self._particles:
            p.update()

        self.update()

    def _fade_in(self) -> None:
        self._fade_timer = QTimer(self)
        self._fade_opacity = 0.0

        def step():
            self._fade_opacity += 0.03
            self.setWindowOpacity(min(1.0, self._fade_opacity))
            if self._fade_opacity >= 1.0:
                self._fade_timer.stop()

        self._fade_timer.timeout.connect(step)
        self._fade_timer.start(16)

    def showMessage(self, message: str, *args, **kwargs) -> None:
        self.current_message = message
        self.update()

    def set_progress(self, value: int) -> None:
        self.current_progress = max(0, min(100, value))
        self.update()

    def finish_loading(self, main_window) -> None:
        self.anim_timer.stop()
        self.set_progress(100)
        QTimer.singleShot(400, lambda: self.finish(main_window))

    def drawContents(self, painter: QPainter) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Particles
        painter.setOpacity(0.6)
        for particle in self._particles:
            particle.draw(painter)
        painter.setOpacity(1.0)

        # Logo
        logo = QPixmap(self.logo_path)
        if not logo.isNull():
            logo_size = 120
            logo_scaled = logo.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_x = (self.width - logo_size) // 2
            logo_y = 80

            glow_size = logo_size * 0.5
            pulse_alpha = 15 + int(10 * math.sin(self.pulse_value))
            glow = QRadialGradient(
                QPointF(logo_x + logo_size / 2, logo_y + logo_size / 2),
                glow_size
            )
            glow.setColorAt(0.0, QColor(0, 217, 255, pulse_alpha))
            glow.setColorAt(0.7, QColor(0, 217, 255, pulse_alpha // 3))
            glow.setColorAt(1.0, Qt.transparent)

            painter.setBrush(glow)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                QPointF(logo_x + logo_size / 2, logo_y + logo_size / 2),
                glow_size, glow_size
            )

            painter.setOpacity(self.logo_opacity)
            painter.drawPixmap(logo_x, logo_y, logo_scaled)
            painter.setOpacity(1.0)

        # Typography
        painter.setOpacity(self.content_opacity)

        painter.setPen(Colors.TEXT_PRIMARY)
        painter.setFont(QFont("Segoe UI", 28, QFont.DemiBold))

        title_y = 230
        painter.drawText(
            QRect(0, title_y, self.width, 40),
            Qt.AlignCenter,
            "ELECDRAFT PRO"
        )

        painter.setPen(Colors.TEXT_SECONDARY)
        painter.setFont(QFont("Segoe UI", 10, QFont.Normal))
        painter.drawText(
            QRect(0, title_y + 42, self.width, 24),
            Qt.AlignCenter,
            "Professional Electrical CAD System"
        )

        # Separator
        sep_y = title_y + 72
        sep_w = 200
        sep_x = (self.width - sep_w) // 2

        sep_grad = QLinearGradient(sep_x, sep_y, sep_x + sep_w, sep_y)
        sep_grad.setColorAt(0.0, Qt.transparent)
        sep_grad.setColorAt(0.5, Colors.BORDER_MEDIUM)
        sep_grad.setColorAt(1.0, Qt.transparent)

        painter.setPen(Qt.NoPen)
        painter.fillRect(QRectF(sep_x, sep_y, sep_w, 1), sep_grad)

        painter.setOpacity(1.0)

        # Progress bar
        bar_x = 180
        bar_y = 330
        bar_w = 360
        bar_h = 3

        bar_rect = QRectF(bar_x, bar_y, bar_w, bar_h)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Colors.BORDER_SUBTLE)
        painter.drawRoundedRect(bar_rect, 1.5, 1.5)

        fill_w = bar_w * self.smooth_progress
        if fill_w > 1:
            fill_rect = QRectF(bar_x, bar_y, fill_w, bar_h)

            fill_grad = QLinearGradient(bar_x, bar_y, bar_x + fill_w, bar_y)
            fill_grad.setColorAt(0.0, Colors.ACCENT_GLOW)
            fill_grad.setColorAt(1.0, Colors.ACCENT_PRIMARY)

            painter.setBrush(fill_grad)
            painter.drawRoundedRect(fill_rect, 1.5, 1.5)

            glow_alpha = 20 + int(10 * math.sin(self.pulse_value))
            painter.setPen(QPen(QColor(0, 217, 255, glow_alpha), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(bar_rect.adjusted(-0.5, -0.5, 0, 0.5), 1.5, 1.5)

        # Status message
        msg_y = bar_y + 28

        painter.setPen(Colors.TEXT_SECONDARY)
        painter.setFont(QFont("Segoe UI", 9, QFont.Normal))

        msg_rect = QRect(0, msg_y, self.width, 20)
        painter.drawText(msg_rect, Qt.AlignCenter, self.current_message)

        ellipsis_count = (int(self.pulse_value * 4) % 4)
        ellipsis = "." * ellipsis_count

        msg_width = painter.fontMetrics().horizontalAdvance(self.current_message)
        painter.drawText(
            self.width // 2 + msg_width // 2 + 2,
            msg_y + 14,
            ellipsis
        )

        # Percentage
        pct_text = f"{int(self.current_progress)}%"
        painter.setPen(Colors.TEXT_TERTIARY)
        painter.setFont(QFont("Segoe UI", 11, QFont.Normal))

        pct_x = bar_x + bar_w + 18
        pct_y = bar_y + 2
        painter.drawText(pct_x, pct_y, pct_text)

        # Footer
        footer_y = self.height - 32

        painter.setPen(Colors.TEXT_DISABLED)
        painter.setFont(QFont("Segoe UI", 8, QFont.Normal))

        painter.drawText(
            QRect(80, footer_y, 300, 20),
            Qt.AlignLeft | Qt.AlignVCenter,
            "PEC 2017 Compliant"
        )

        painter.setPen(Colors.TEXT_TERTIARY)
        painter.drawText(
            QRect(0, footer_y, self.width, 20),
            Qt.AlignCenter,
            "Version 2.5.0"
        )

        painter.setPen(Colors.TEXT_DISABLED)
        painter.drawText(
            QRect(self.width - 380, footer_y, 300, 20),
            Qt.AlignRight | Qt.AlignVCenter,
            "© 2025 ELECDRAFT"
        )

        # Accent line
        accent_grad = QLinearGradient(0, 0, self.width, 0)
        accent_grad.setColorAt(0.0, Qt.transparent)
        accent_grad.setColorAt(0.3, QColor(0, 217, 255, 80))
        accent_grad.setColorAt(0.7, QColor(0, 217, 255, 80))
        accent_grad.setColorAt(1.0, Qt.transparent)

        painter.fillRect(QRectF(0, 0, self.width, 1), accent_grad)