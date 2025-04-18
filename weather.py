import requests
from configparser import ConfigParser

class Weather:
    def __init__(self):
        try:
            self.config = ConfigParser()
            self.config.read("config/config.ini")
            api_key = self.config.get("Panel", "weather_api_key")
            city = self.config.get("Panel", "city")
            
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
            self.response = requests.get(url)
            self.data = self.response.json()

        except Exception as e:
            print("Error", e)
    def get_city(self):
        try: 
            self.city = self.config.get("Panel", "city")
            return self.city
        except Exception as e:
            print("Error", e)
            self.city = ""
            return self.city

    def get_temp(self):
        try:
            if 'main' in self.data:
                temp = self.data['main']['temp']
                temp -= 273
                return f"Temperature: {temp:.2f} °C"
            else:
                return "Temperature data not available"
        except Exception as e:
            print("Error", e)
            return 'Temperature data not available'

    def get_sky(self):
        try:
            description = self.data['weather'][0]['description']
        except Exception as e:
            print("Error", e)
            description = ""

        return f"Sky: {description}"
