from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QWidget
from PyQt6.QtGui import QIcon, QAction, QCursor
from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtWidgets import QSystemTrayIcon as TrayActivationReason
from gui.small_gui import SmallTrayWindow
from gui.full_gui import FullWindow  # Placeholder if not implemented
from logger_manager import LoggerManager
import os

logger = LoggerManager().get_logger()

class TrayIconManager(QWidget):
    def __init__(self, app, on_start, on_stop, on_quit):
        super().__init__()
        self.app = app
        self.icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path), parent=app)
        self.tray_icon.setToolTip("Work Hours Tracker")

        self.menu = QMenu()
        self.start_action = QAction("Start Work")
        self.stop_action = QAction("Stop Work")
        self.quit_action = QAction("Quit")
        self.menu.addAction(self.start_action)
        self.menu.addAction(self.stop_action)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.menu)

        self.start_action.triggered.connect(on_start)
        self.stop_action.triggered.connect(on_stop)
        self.quit_action.triggered.connect(on_quit)
        self.tray_icon.activated.connect(self.handle_click)

        self.small_window = SmallTrayWindow()
        self.small_window.start_button.clicked.connect(on_start)
        self.small_window.finish_button.clicked.connect(on_stop)
        self.small_window.break_button.clicked.connect(self.handle_break)

        self.full_window = FullWindow()

    def show(self):
        self.tray_icon.show()

    def show_message(self, title, message):
        self.tray_icon.showMessage(title, message)

    def handle_click(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.Context):
            cursor_pos = QCursor.pos()
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry: QRect = screen.availableGeometry()
                window_size = self.small_window.size()

                # Position the window above the cursor (tray icon) with a vertical offset
                x = cursor_pos.x() - window_size.width() // 2
                y = cursor_pos.y() - window_size.height() - 70  # Apply vertical offset

                # Adjust to ensure the window is fully visible on screen
                if x < screen_geometry.left():
                    x = screen_geometry.left()
                elif x + window_size.width() > screen_geometry.right():
                    x = screen_geometry.right() - window_size.width()

                if y < screen_geometry.top():
                    y = screen_geometry.top()
                elif y + window_size.height() > screen_geometry.bottom():
                    y = screen_geometry.bottom() - window_size.height()

                self.small_window.move(QPoint(x, y))

            self.small_window.show()
            self.small_window.raise_()
            self.small_window.activateWindow()
        elif reason == TrayActivationReason.ActivationReason.DoubleClick:
            self.show_full_gui()

    def show_full_gui(self):
        logger.info("Double-click detected: Full GUI should be shown.")
        self.small_window.hide()
        self.full_window.show()
        self.full_window.raise_()
        self.full_window.activateWindow()

    def handle_break(self):
        logger.info("Break Time clicked from tray.")
        self.tray_icon.showMessage("Break Time", "Break time started.")


