#this class is use to get users wifi to see if its connected to the internet,
#so it can display the wifi icon.
import subprocess
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QTimer


class ConnectedToWifi:
    @staticmethod
    def is_wifi_connected():
        try:
            # Execute the netsh wlan command to get details of the current connection
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True
            )

            # Check if the command executed successfully
            if result.returncode == 0:
                # Look for the "State" line in the command output
                for line in result.stdout.split("\n"):
                    if "State" in line:
                        state = line.split(":")[1].strip()
                        return state == "connected"
            else:
                print("Failed to execute the command.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return False

    @staticmethod
    def get_connected_wifi_ssid():
        try:
            # Execute the netsh wlan command to get details of the current connection
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True
            )

            # Check if the command executed successfully
            if result.returncode == 0:
                # Look for the SSID line in the command output
                for line in result.stdout.split("\n"):
                    if "SSID" in line and "BSSID" not in line:
                        # Extract and return the SSID
                        return line.split(":")[1].strip()
        except Exception as e:
            print(f"An error occurred: {e}")

        return None