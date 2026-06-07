import requests

class DarkWetherError(Exception): pass

class TemporaryWether:
    def __init__(self, api_key, city=None):
        self.api_key = api_key
        self.city = city
    
    def __str__(self):
        return str(self.api_key)

def initialization(api_key):
    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q=London")
    if response.status_code != 200:
        raise DarkWetherError('weather.initialization(): неверный ApiKey')
    else:
        return TemporaryWether(api_key)
    
def get_weather(initialization, city):
    if not isinstance(initialization, TemporaryWether):
        raise DarkWetherError('weather.get_weather(): тип initialization неверен')
    api_key = initialization.api_key

    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}")
    if response.status_code != 200:
        raise DarkWetherError(f'weather.get_weather(): Статус - {response.status_code}')
    else:
        return response