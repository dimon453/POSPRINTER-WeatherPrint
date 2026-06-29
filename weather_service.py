"""
Модуль получения погоды из OpenWeatherMap
"""
import requests
from datetime import datetime

def get_weather(city, api_key):
    """
    Получить данные погоды для города
    
    Args:
        city: Название города (например, "Chișinău")
        api_key: API ключ OpenWeatherMap
    
    Returns:
        dict с данными погоды или None если ошибка
    """
    try:
        # API endpoint
        url = "https://api.openweathermap.org/data/2.5/weather"
        
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric',  # Цельсий
            'lang': 'ru'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Парсим нужные данные
        weather = {
            'city': data.get('name', city),
            'country': data.get('sys', {}).get('country', ''),
            'description': data.get('weather', [{}])[0].get('main', 'Unknown'),
            'description_ru': data.get('weather', [{}])[0].get('description', 'неизвестно'),
            'temp': round(data.get('main', {}).get('temp', 0)),
            'temp_min': round(data.get('main', {}).get('temp_min', 0)),
            'temp_max': round(data.get('main', {}).get('temp_max', 0)),
            'feels_like': round(data.get('main', {}).get('feels_like', 0)),
            'humidity': data.get('main', {}).get('humidity', 0),
            'wind_speed': round(data.get('wind', {}).get('speed', 0), 1),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'raw': data
        }
        
        return weather
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к OpenWeatherMap: {e}")
        return None
    except Exception as e:
        print(f"Ошибка парсинга погоды: {e}")
        return None

def get_weather_icon_ascii(description):
    """
    Получить ASCII иконку по описанию погоды
    
    Args:
        description: Строка описания погоды (например, "Clear", "Rainy")
    
    Returns:
        ASCII арт иконка
    """
    icons = {
        'Clear': [
            "   /\\    ",
            "  /  \\   ",
            " |    |  ",
            "  \\  /   ",
            "   \\/    "
        ],
        'Clouds': [
            " _____    ",
            "|  O  |   ",
            "|_____|   "
        ],
        'Rain': [
            " _____    ",
            "|  O  |   ",
            "|' ' '|   ",
            " ' ' '    "
        ],
        'Snow': [
            " _____    ",
            "| * * |   ",
            "|* * *|   ",
            " * * *    "
        ],
        'Thunderstorm': [
            " _____    ",
            "| / \\ |   ",
            "|/ \\ |    ",
            " / \\     "
        ],
        'Drizzle': [
            " _____    ",
            "|  ~  |   ",
            "|~ ~ ~|   ",
            " ~ ~ ~    "
        ],
        'Mist': [
            " ~ ~ ~    ",
            "~ ~ ~ ~   ",
            " ~ ~ ~    "
        ]
    }
    
    # Найти иконку по ключевому слову
    for key, icon in icons.items():
        if key.lower() in description.lower():
            return icon
    
    # По умолчанию облака
    return icons['Clouds']
