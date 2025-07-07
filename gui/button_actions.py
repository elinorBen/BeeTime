from PyQt6.QtCore import QTime
from core.startup_manager import StartupManager
from core.activity_manager import ActivityManager
from core.work_log_manager import WorkLogManager
from services.notification_manager import WorkDialogManager
from logger_manager import LoggerManager

startup = StartupManager()


def handle_start_work(widget=None):
    startup.attempt_start_work_session(skip_quit=True)
    if widget:
        widget.hide()


def handle_finish_work(widget=None):
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
        manager.end_last_session(end_time=now, type="finish")
        activity_manager.stop_all_monitors()
        manager.send_summary()
        logger.info("Workday finished and summary sent.")
    else:
        logger.info("User cancelled finishing workday.")

    if widget:
        widget.hide()


def handle_break(widget=None):
    logger = LoggerManager().get_logger()
    logger.debug("Break Time button clicked.")

    dialog = WorkDialogManager()
    note = dialog.show_break_dialog() or "break button"

    now = QTime.currentTime().toString("HH:mm")
    manager = WorkLogManager()
    manager.end_last_session(end_time=now, type="break")
    manager.add_inactive_period(start=now, end=None, note=note)

    activity_manager = ActivityManager(manager)
    activity_manager.start_monitoring_activity()

    logger.info(f"Break started at {now} with note: {note}")

    if widget:
        widget.hide()

