import sys
from PyQt6.QtWidgets import QApplication
from core.startup_manager import StartupManager
from core.activity_manager import ActivityManager
from tray_icon_manager import TrayIconManager
from datetime import datetime
from logger_manager import LoggerManager

logger = LoggerManager().get_logger()

def main():
    app = QApplication(sys.argv)
    startup = StartupManager()
    # Run startup sequence
    manager, location = startup.run_startup_sequence(app)
    if manager is None:
        return  # User cancelled startup

    # Setup activity monitoring and summary timer
    activity_manager = ActivityManager(manager)
    activity_manager.setup_activity_monitor()
    manager.summary_timer = activity_manager.setup_summary_timer()

    # Define tray icon actions
    def start_work():
        logger.info("Start Work clicked from tray.")

    def stop_work():
        logger.info("Stop Work clicked from tray.")

    def quit_app():
        logger.info("Quitting application from tray.")
        app.quit()

    # Launch tray icon
    tray = TrayIconManager(app,  start_work, stop_work, quit_app)
    tray.show()
    tray.show_message("Work Hours Tracker", "App is running in the background.")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
