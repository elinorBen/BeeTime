import json
import os
from datetime import datetime, timedelta
from logger_manager import LoggerManager

logger = LoggerManager().get_logger()

class WorkLogManager:
    def __init__(self, log_file='work_log.json', required_hours=8.8):
        self.log_file = log_file
        self.required_time = self._minutes_to_hhmm(int(required_hours * 60))
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.data = self._load()
        self._ensure_today_entry()

    def _load(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def _ensure_today_entry(self):
        if self.today not in self.data:
            self.data[self.today] = {
                "work_location": None,
                "required_time": self.required_time,
                "sessions": [],
                "inactive_periods": [],
                "summary": {
                    "missing_time": self.required_time,
                    "total_tracked": "00:00",
                    "total_inactive": "00:00",
                    "manual_adjustments": "00:00",
                    "total_reported": "00:00",
                    "overtime": "00:00",
                    "met_target": False
                }
            }

    def update_field(self, path, value):
        keys = path.split('.')
        ref = self.data
        for key in keys[:-1]:
            ref = ref.setdefault(key, {})
        ref[keys[-1]] = value
        self._save()

    def add_session(self, start_time, end_time=None, note=None, source="auto", session_type="start", location=None):
        sessions = self.data[self.today]["sessions"]

        if session_type == "start":
            for session in sessions:
                if session.get("type") == "start" and session.get("start_time") == start_time and session.get("source") == source:
                    return  # Skip adding duplicate

        session = {
            "start_time": start_time,
            "end_time": end_time,
            "source": source,
            "type": session_type
        }

        if note:
            session["note"] = note

        sessions.append(session)     

        if location:
            self.data[self.today]["work_location"] = location

        self._save()

    def add_inactive_period(self, start, end=None, note=None):
        period = {"start_time": start, "end_time": end}
        if note:
            period["note"] = note
        self.data[self.today]["inactive_periods"].append(period)
        self._save()

    def _minutes_to_hhmm(self, minutes):
        return f"{minutes // 60:02}:{minutes % 60:02}"

    def _hhmm_to_minutes(self, hhmm):
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    def calculate_summary(self):
        sessions = self.data[self.today]["sessions"]
        inactive_periods = self.data[self.today]["inactive_periods"]
        summary = self.data[self.today]["summary"]

        total_tracked = 0
        for session in sessions:
            try:
                start = datetime.strptime(session["start_time"], "%H:%M")
                if "end_time" in session and session["end_time"]:
                    end = datetime.strptime(session["end_time"], "%H:%M")
                else:
                    now = datetime.now()
                    end = datetime.strptime(now.strftime("%H:%M"), "%H:%M")
                duration = (end - start).total_seconds() / 60
                total_tracked += max(0, int(duration))
            except ValueError:
                continue

        total_inactive = 0
        for period in inactive_periods:
            try:
                start = datetime.strptime(period["start_time"], "%H:%M")
                if period["end_time"]:
                    end = datetime.strptime(period["end_time"], "%H:%M")
                duration = (end - start).total_seconds() / 60
                total_inactive += max(0, int(duration))
            except ValueError:
                continue

        manual_adjustments = self._hhmm_to_minutes(summary.get("manual_adjustments", "00:00"))
        required_minutes = self._hhmm_to_minutes(self.data[self.today]["required_time"])
        total_reported = total_tracked + manual_adjustments
        overtime = max(0, total_reported - required_minutes)
        missing_minutes = max(0, required_minutes - total_reported)
        logger.info(f"You have left {self._minutes_to_hhmm(missing_minutes)} hours to work")
        met_target = total_reported >= required_minutes

        summary.update({
            "missing_time": self._minutes_to_hhmm(missing_minutes),
            "total_tracked": self._minutes_to_hhmm(total_tracked),
            "total_inactive": self._minutes_to_hhmm(total_inactive),
            "total_reported": self._minutes_to_hhmm(total_reported),
            "overtime": self._minutes_to_hhmm(overtime),
            "met_target": met_target
        })

        self._save()

    def end_last_session(self, end_time, type=None):
        sessions = self.data[self.today]["sessions"]
        for session in reversed(sessions):
            if "end_time" not in session or session["end_time"] in (None, "", "null"):
                session["end_time"] = end_time
                if type:
                    session["type"] = type
                break
        self._save()

    def handle_idle(self, reason):
        logger.info(f"User is {reason}")
        now = datetime.now().strftime("%H:%M")
        self.end_last_session(end_time=now)
        self.add_inactive_period(start=now, note=reason)

    def handle_active(self):
        logger.info(f"User is back to activity")
        now = datetime.now().strftime("%H:%M")
        if self.data[self.today]["inactive_periods"]:
            self.data[self.today]["inactive_periods"][-1]["end_time"] = now
        self._save()
        self.add_session(start_time=now, note="back from break", source="auto", session_type="activity")

    def get_today_log(self):
        return self.data[self.today]

    def has_session(self, session_type: str) -> bool:
        return any(s.get("type") == session_type for s in self.data[self.today]["sessions"])

    def check_target_met(self):
        target_minutes = self._hhmm_to_minutes(self.data[self.today]["required_time"])
        total_minutes = self._hhmm_to_minutes(self.data[self.today]["summary"]["total_reported"])
        remaining = max(0, target_minutes - total_minutes)
        return total_minutes >= target_minutes, remaining

    def get_today_value(self, key: str, convert_to_minutes: bool = False):
        if key == "start_time":
            value = next((s["start_time"] for s in self.data[self.today]["sessions"] if s.get("type") == "start"), None)
        else:
            value = self.data.get(self.today, {}).get(key)
        if convert_to_minutes and isinstance(value, str) and ':' in value:
            return self._hhmm_to_minutes(value)
        return value

    def send_summary(self):
        self.calculate_summary()
        summary = self.data[self.today]["summary"]
        logger.info("Daily Summary:")
        for key, value in summary.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")



