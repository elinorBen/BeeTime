import os
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QTime
from core.startup_manager import StartupManager
from core.activity_manager import ActivityManager
from core.work_log_manager import WorkLogManager
from services.notification_manager import WorkDialogManager
from logger_manager import LoggerManager
from gui.button_actions import handle_start_work, handle_finish_work, handle_break

startup = StartupManager()

class SmallTrayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BeeTime")
        self.setFixedSize(260, 360)
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("""
        QWidget {
            background-color: #f8f8f0;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        QPushButton {
            font-size: 14px;
            padding: 8px;
            border-radius: 6px;
        }
        QPushButton#start {
            background-color: #a8d5a2;
            color: #2e2e2e;
        }
        QPushButton#finish {
            background-color: #cccccc;
            color: #2e2e2e;
        }
        QPushButton#break {
            background-color: #ffe680;
            color: #2e2e2e;
        }
        """)

        layout = QVBoxLayout()
        image_path = os.path.join(os.path.dirname(__file__), "..", "assets", "bee_time.png")
        if os.path.exists(image_path):
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaledToWidth(244, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)

        self.start_button = QPushButton("Start Work Day")
        self.start_button.setObjectName("start")
        layout.addWidget(self.start_button)

        self.finish_button = QPushButton("Finish Work Day")
        self.finish_button.setObjectName("finish")
        layout.addWidget(self.finish_button)

        self.break_button = QPushButton("Break Time")
        self.break_button.setObjectName("break")
        layout.addWidget(self.break_button)

        self.setLayout(layout)

        self.start_button.clicked.connect(lambda: handle_start_work(self))
        self.finish_button.clicked.connect(lambda: handle_finish_work(self))
        self.break_button.clicked.connect(lambda: handle_break(self))

    def handle_start_work(self):
        startup.attempt_start_work_session(skip_quit=True)
        self.hide()

    def handle_finish_work(self):
        logger = LoggerManager().get_logger()
        logger.debug("Finish Work Day button clicked.")

        manager = WorkLogManager()
        activity_manager = ActivityManager(manager)
        dialog = WorkDialogManager()

        met_target, remaining = manager.check_target_met()
        if met_target:
            confirmed = dialog.show_finish_dialog_met_target()
        else:
            hours = remaining // 60
            minutes = remaining % 60
            remaining_str = f"{hours:02}:{minutes:02}"
            confirmed = dialog.show_finish_dialog_not_met_target(remaining_str)

        if confirmed:
            now = QTime.currentTime().toString("HH:mm")
            manager.end_last_session(end_time=now)
            activity_manager.stop_all_monitors()
            manager.send_summary()
            logger.info("Workday finished and summary sent.")
        else:
            logger.info("User cancelled finishing workday.")

        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
