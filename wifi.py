#this class is use to get users wifi to see if its connected to the internet,
#so it can display the wifi icon.

import requests

class ConnectedToWifi:
    @staticmethod
    def is_connectToInternet():
        try:
            response = requests.get("https://www.google.com", timeout=2)
            return response.status_code == 200
        except requests.ConnectionError:
            return False
