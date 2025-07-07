# core/startup_manager.py

from PyQt6.QtCore import QTimer
from services.network_detector import NetworkDetector
from services.notification_manager import WorkDialogManager
from core.work_log_manager import WorkLogManager
from logger_manager import LoggerManager

class StartupManager:
    def __init__(self):
        self.logger = LoggerManager().get_logger()
        self.manager = WorkLogManager()
        self.work_dialog_manager = WorkDialogManager()

    def attempt_start_work_session(self, skip_quit=False, app=None):
        if self.manager.has_session("start"):
            self.logger.info("Start session already exists for today. Skipping start work dialog.")
            return None, None

        location = NetworkDetector().get_work_location()
        confirmed_time = self.work_dialog_manager.show_start_work_dialog(location)
        if confirmed_time:
            self.manager.add_session(start_time=confirmed_time, source="auto", session_type="start", location=location)
            self.logger.info(f"Work session started at {confirmed_time} from {location}")
            return self.manager, location
        else:
            self.logger.info("User cancelled start work dialog.")
            if not skip_quit and app is not None:
                QTimer.singleShot(1000, app.quit)
            return None, None

    def run_startup_sequence(self, app):
        if self.manager.has_session("start"):
            self.logger.info("Start session already exists for today. Skipping start work dialog.")
            location = self.manager.get_today_log().get("work_location", "unknown")
            return self.manager, location
        return self.attempt_start_work_session(skip_quit=False, app=app)
