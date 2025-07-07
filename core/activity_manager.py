from PyQt6.QtCore import QTimer
from services.activity_monitor import ActivityMonitor

class ActivityManager:
    def __init__(self, work_log_manager, idle_threshold_seconds=300):
        self.manager = work_log_manager
        self.idle_threshold_seconds = idle_threshold_seconds
        self.monitor = None
        self.summary_timer = None

    def setup_activity_monitor(self):
        def on_idle(reason):
            self.manager.handle_idle(reason)

        def on_active():
            self.manager.handle_active()

        self.monitor = ActivityMonitor(
            idle_threshold_seconds=self.idle_threshold_seconds,
            on_idle_start=on_idle,
            on_idle_end=on_active
        )
        self.monitor.start()

    def setup_summary_timer(self):
        self.summary_timer = QTimer()
        self.summary_timer.timeout.connect(self.manager.calculate_summary)
        self.summary_timer.start(60 * 1000)  # every 60 seconds
        return self.summary_timer

    def stop_all_monitors(self):
        if self.monitor:
            self.monitor.stop()
        if self.summary_timer:
            self.summary_timer.stop()

    def start_monitoring_activity(self):
        if not self.monitor:
            self.setup_activity_monitor()
        elif not self.monitor.is_monitoring_active():
            self.monitor.start()
