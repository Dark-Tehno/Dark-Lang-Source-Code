import requests
from dark_code.dark_exceptions import DarkError

class DarkWetherError(DarkError): pass

class TemporaryWether:
    def __init__(self, api_key, city=None):
        self.api_key = api_key
        self.city = city
    
    def __str__(self):
        return str(self.api_key)

def native_weather_initialization(args):
    if len(args) != 1:
        raise DarkWetherError("weather.initialization() принимает ровно 1 аргумент (ApiKey)")
    
    api_key = args[0]

    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q=London")
    if response.status_code != 200:
        raise DarkWetherError('weather.initialization(): неверный ApiKey')
    else:
        return TemporaryWether(api_key)
    
def native_weather_get_weather(args):
    if len(args) != 2:
        raise DarkWetherError("weather.get_weather() принимает 2 аргумента (initialization, city)")

    initialization = args[0]
    if not isinstance(initialization, TemporaryWether):
        raise DarkWetherError('weather.get_weather(): тип initialization неверен')
    city = args[1]
    api_key = initialization.api_key

    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}")
    if response.status_code != 200:
        raise DarkWetherError(f'weather.get_weather(): Статус - {response.status_code}')
    else:
        return response