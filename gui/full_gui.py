from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPalette, QColor
from datetime import datetime, timedelta
from core.activity_manager import ActivityManager
from core.work_log_manager import WorkLogManager
from gui.styles import BUTTON_STYLE_GREEN, BUTTON_STYLE_GRAY, BUTTON_STYLE_OFFWHITE
from gui.button_actions import handle_start_work, handle_finish_work, handle_break

class FullWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BeeTime - Full Dashboard")
        self.setFixedSize(420, 270)
        self.setWindowIcon(QIcon("assets/icon.ico"))

        self.manager = WorkLogManager()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.start_time, self.location, self.required_hours = self.get_labels_data()

        # Clean background
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f8f8f0"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Top section: date, status, location
        top_layout = QHBoxLayout()
        self.date_label = QLabel(f"📅 {self.today}")
        self.date_label.setStyleSheet("font-size: 13px; color: #333;")
        top_layout.addWidget(self.date_label)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 13px; color: #2e2e2e;")
        top_layout.addStretch()
        top_layout.addWidget(self.status_label)

        self.location_label = QLabel()
        self.location_label.setStyleSheet("font-size: 13px; color: #2e2e2e;")
        top_layout.addWidget(self.location_label)

        layout.addLayout(top_layout)
        self.update_status_label()

        # Timer section
        self.timer_label = QLabel("Time remaining: calculating...")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 14px; color: #2e2e2e;")
        layout.addWidget(self.timer_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_remaining)
        self.timer.start(1000)

        # Main buttons
        main_button_layout = QHBoxLayout()

        self.start_button = QPushButton("▶ Start Work Day")
        self.start_button.setStyleSheet(BUTTON_STYLE_GREEN + " padding: 6px; font-size: 12px; border-radius: 6px;")
        main_button_layout.addWidget(self.start_button)

        self.finish_button = QPushButton("⏹ Finish Work Day")
        self.finish_button.setStyleSheet(BUTTON_STYLE_GRAY + " padding: 6px; font-size: 12px; border-radius: 6px;")
        main_button_layout.addWidget(self.finish_button)

        self.break_button = QPushButton("☕ Break Time")
        self.break_button.setStyleSheet(BUTTON_STYLE_OFFWHITE + " padding: 6px; font-size: 12px; border-radius: 6px;")
        main_button_layout.addWidget(self.break_button)

        layout.addLayout(main_button_layout)

        # Preferences button
        self.settings_button = QPushButton("⚙ Preferences")
        self.settings_button.setStyleSheet(BUTTON_STYLE_OFFWHITE + " padding: 6px; font-size: 12px; border-radius: 6px;")
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Button actions
        self.start_button.clicked.connect(lambda: handle_start_work(self))
        self.finish_button.clicked.connect(lambda: handle_finish_work(self))
        self.break_button.clicked.connect(lambda: handle_break(self))

        self.setLayout(layout)

    def update_status_label(self):
        active = self.start_time and not (self.manager.has_session("finish"))
        status = "🟢 Active" if active else "⚪ Inactive"
        self.status_label.setText(status)
        self.location_label.setText(f"🏠 {self.location}")

    def update_time_remaining(self):
        now = datetime.now()
        try:
            parsed_start_time = datetime.strptime(self.start_time, "%H:%M")
            parsed_start_time = parsed_start_time.replace(year=now.year, month=now.month, day=now.day)
        except Exception:
            parsed_start_time = now
        elapsed = now - parsed_start_time
        remaining = max(timedelta(), timedelta(hours=self.required_hours) - elapsed)
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes = remainder // 60
        self.timer_label.setText(f"Time remaining: {hours:02d}:{minutes:02d}")

    def get_labels_data(self):
        location = self.manager.get_today_value("work_location")
        required_minutes = self.manager.get_today_value("required_time", convert_to_minutes=True)
        required_hours = required_minutes / 60
        start_time = self.manager.get_today_value("start_time", convert_to_minutes=False)
        return start_time, location, required_hours

    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Preferences")
        dialog.setFixedSize(300, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Customization settings go here..."))
        dialog.setLayout(layout)
        dialog.exec()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
