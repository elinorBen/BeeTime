
import ctypes
import subprocess
import threading
import time
from logger_manager import LoggerManager
logger = LoggerManager().get_logger()

class ActivityMonitor:
    def __init__(self, idle_threshold_seconds=300, on_idle_start=None, on_idle_end=None):
        self.idle_threshold = idle_threshold_seconds
        self.on_idle_start = on_idle_start
        self.on_idle_end = on_idle_end
        self._is_idle = False
        self._stop_event = threading.Event()
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.last_mouse_position = pyautogui.position()
        except Exception as e:
            logger.warning("pyautogui not available: %s", e)
            self.pyautogui = None

    def _get_idle_duration(self):
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
        last_input_info = LASTINPUTINFO()
        last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info)):
            millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
            return millis / 1000.0
        return 0

    def _is_workstation_locked(self):
        try:
            result = subprocess.check_output(
                ['powershell', '-Command',
                 '(Get-Process -Name LogonUI -ErrorAction SilentlyContinue) -ne $null'],
                stderr=subprocess.DEVNULL
            )
            return result.strip() == b'True'
        except Exception as e:
            logger.error(f"Error checking lock status: {e}")
            return False

    def _check_mouse_movement(self):
        if self.pyautogui:
            try:
                current_position = self.pyautogui.position()
                if current_position != self.last_mouse_position:
                    self.last_mouse_position = current_position
                    return True
            except Exception:
                pass
        return False

    def _monitor(self):
        while not self._stop_event.is_set():
            idle_time = self._get_idle_duration()
            locked = self._is_workstation_locked()
            mouse_moved = self._check_mouse_movement()

            if (idle_time > self.idle_threshold or locked) and not self._is_idle:
                self._is_idle = True
                if self.on_idle_start:
                    self.on_idle_start("locked" if locked else "idle")
            elif (idle_time <= self.idle_threshold and not locked and mouse_moved) and self._is_idle:
                self._is_idle = False
                if self.on_idle_end:
                    self.on_idle_end()
            time.sleep(5)

    def start(self):
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()

    def is_monitoring_active(self):
        return self.thread.is_alive() if hasattr(self, 'thread') else False
