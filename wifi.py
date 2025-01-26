#this class is use to get users wifi to see if its connected to the internet,
#so it can display the wifi icon.
import subprocess

class ConnectedToWifi:
    @staticmethod
    def is_wifi_connected():
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
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
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "SSID" in line and "BSSID" not in line:
                        return line.split(":")[1].strip()
        except Exception as e:
            print(f"An error occurred: {e}")

        return None