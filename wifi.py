#this class is use to get users wifi to see if its connected to the internet,
#so it can display the wifi icon.
import subprocess
import requests

class ConnectedToWifi:
    @staticmethod
    def is_connectToInternet():
        try:
            response = requests.get("https://www.google.com")
            return response.status_code == 200
        except requests.ConnectionError:
            return False

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
            else:
                print("Failed to execute the command.")
        except Exception as e:
            print(f"An error occurred: {e}")

        return None

# print(ConnectedToWifi.get_connected_wifi_ssid())