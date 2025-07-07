
import subprocess
import platform
from logger_manager import LoggerManager
logger = LoggerManager().get_logger()

class NetworkDetector:
    """
    Detects the user's work location based on network connection.
    Determines if the user is working from home (VPN) or from the office (WiFi).
    """

    def __init__(self):
        self.office_wifi_name = "AmdocsSeamless"
        self.vpn_identifiers = [
            "_Common_Amdocs-FullVPN-DIRECT-NetworkAccess",
            "corp.amdocs.com"
            ]

    def is_connected_to_vpn(self):
        """
        Checks if the user is connected to the VPN by analyzing the output of ipconfig.
        Returns True if VPN identifiers are found, False otherwise.
        """
        try:
            output = subprocess.check_output("ipconfig", encoding="utf-8")
            logger.debug("Checking VPN connection...")
            return all(identifier in output for identifier in self.vpn_identifiers)
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to check VPN connection: {e}")
            return False

    def is_connected_to_office_wifi(self):
        """
        Checks if the user is connected to the office WiFi.
        Returns True if connected to the specified WiFi network.
        """
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output("netsh wlan show interfaces", encoding="utf-8")
                logger.debug("Checking WiFi connection...")
                return self.office_wifi_name in output
            else:
                logger.warning("WiFi detection is only implemented for Windows.")
                return False
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to check WiFi connection: {e}")
            return False

    def get_work_location(self):
        """
        Determines the user's work location.
        Returns 'home' if connected to VPN, 'office' if connected to office WiFi, or 'unknown'.
        """
        if self.is_connected_to_vpn():
            logger.info("Found Connection! Connected Amdocs network via VPN")
            return "Home"
        elif self.is_connected_to_office_wifi():
            logger.info("Found Connection! Connected Amdocs network via LAN")
            return "Office"
        else:
            logger.info("Failed to find connection to AMDOCS network")
            return "unknown"
