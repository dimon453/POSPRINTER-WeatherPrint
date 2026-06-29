"""
Примеры расширения приложения "Погода на Чеке"
"""

# ============================================================================
# ПРИМЕР 1: Добавить прогноз на несколько дней
# ============================================================================

def get_weather_forecast(city, api_key, days=3):
    """
    Получить прогноз на несколько дней
    """
    import requests
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'ru'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        forecasts = []
        # Берем каждое предсказание через 24 часа
        for i in range(0, len(data['list']), 8):  # 8 * 3часа = 24часа
            if len(forecasts) >= days:
                break
            
            item = data['list'][i]
            forecasts.append({
                'date': item['dt_txt'].split()[0],
                'temp_min': round(item['main']['temp_min']),
                'temp_max': round(item['main']['temp_max']),
                'description': item['weather'][0]['main'],
                'description_ru': item['weather'][0]['description']
            })
        
        return forecasts
    except Exception as e:
        print(f"Ошибка прогноза: {e}")
        return []

# Использование в receipt_formatter.py:
"""
def format_receipt_with_forecast(weather_data, forecast_data, tape_width_mm=60):
    lines = []
    # ... существующий код ...
    
    # Добавить прогноз
    lines.append("\nПрогноз на 3 дня:")
    lines.append("-" * width)
    
    for day in forecast_data:
        line = f"{day['date']}: {day['description_ru']}"
        line += f" {day['temp_min']}..{day['temp_max']}°C"
        lines.append(line)
    
    return "\n".join(lines)
"""

# ============================================================================
# ПРИМЕР 2: Расширить форматы ширины ленты
# ============================================================================

# В receipt_formatter.py, функция format_receipt():

width_map = {
    32: 32,    # 32мм принтер
    40: 40,    # 40мм принтер
    58: 46,    # 58мм принтер (POS895UE)
    60: 48,    # 60мм принтер
    80: 64,    # 80мм принтер
}

# Если нужен промежуточный размер:
# 35: 35, 45: 45, 55: 55

# ============================================================================
# ПРИМЕР 3: Добавить поддержку нескольких городов
# ============================================================================

def format_multi_city_receipt(cities_weather, tape_width_mm=60):
    """
    Печать погоды для нескольких городов на одном чеке
    """
    width_map = {60: 48}
    width = width_map.get(tape_width_mm, 48)
    
    lines = []
    lines.append("=" * width)
    lines.append("ПОГОДА В НЕСКОЛЬКИХ ГОРОДАХ".center(width))
    lines.append("=" * width)
    lines.append("")
    
    for city_name, weather in cities_weather.items():
        lines.append(f"{city_name}:")
        lines.append(f"  Темп: {weather['temp']}°C (ощущается {weather['feels_like']}°C)")
        lines.append(f"  {weather['description_ru']}")
        lines.append(f"  Влаж: {weather['humidity']}% | Ветер: {weather['wind_speed']}м/с")
        lines.append("")
    
    lines.append("=" * width)
    return "\n".join(lines)

# Использование:
"""
cities = {
    'Chișinău': get_weather('Chișinău', api_key),
    'Bucharest': get_weather('Bucharest', api_key),
    'Kyiv': get_weather('Kyiv', api_key)
}
text = format_multi_city_receipt(cities)
print_receipt(text, printer_name)
"""

# ============================================================================
# ПРИМЕР 4: Добавить кастомные ASCII иконки
# ============================================================================

def get_custom_weather_icons():
    """
    Расширенный набор иконок погоды
    """
    return {
        'sunny': [
            "      ☀      ",
            "    ☀   ☀    ",
            "   ☀     ☀   ",
            "    ☀   ☀    ",
            "      ☀      "
        ],
        'cloudy': [
            "   ☁  ☁     ",
            "  ☁    ☁    ",
            " ☁      ☁   ",
            "  ☁    ☁    ",
            "   ☁  ☁     "
        ],
        'rainy': [
            "   ☁  ☁     ",
            "  ☁ ~ ☁    ",
            " ☁ ~ ~ ☁   ",
            "  ☁ ~ ☁    ",
            "   ~ ~ ~    "
        ],
        'snowy': [
            "   ☁  ☁     ",
            "  ☁ ❄ ☁    ",
            " ☁ ❄ ❄ ☁   ",
            "  ☁ ❄ ☁    ",
            "   ❄ ❄ ❄   "
        ],
        'thunderstorm': [
            "  ☁⚡☁     ",
            " ☁ ⚡ ☁    ",
            "☁   ⚡   ☁  ",
            " ☁ ⚡ ☁    ",
            "  ☁ ⚡ ☁   "
        ]
    }

# ============================================================================
# ПРИМЕР 5: Добавить логирование всех печатей
# ============================================================================

import json
from datetime import datetime

def log_print_event(weather_data, success, printer_name):
    """
    Логировать каждую печать
    """
    log_file = 'print_log.json'
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'city': weather_data.get('city'),
        'temperature': weather_data.get('temp'),
        'description': weather_data.get('description_ru'),
        'printer': printer_name,
        'success': success
    }
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except:
        pass

# Вызвать в weather_bot.py после print_receipt():
"""
log_print_event(weather_data, success, printer_name)
"""

# ============================================================================
# ПРИМЕР 6: Добавить отправку уведомлений
# ============================================================================

def send_notification_telegram(message, bot_token, chat_id):
    """
    Отправить уведомление в Telegram
    """
    import requests
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
        return True
    except:
        return False

# Использование в weather_bot.py:
"""
if success:
    msg = f"Погода для {weather_data['city']}: {weather_data['temp']}°C"
    send_notification_telegram(msg, BOT_TOKEN, CHAT_ID)
"""

# ============================================================================
# ПРИМЕР 7: Добавить веб-просмотр последних печатей
# ============================================================================

# В weather_printer_app.py:

@app.route('/api/print-history', methods=['GET'])
def get_print_history():
    """
    Получить историю последних печатей из логов
    """
    import json
    
    history = []
    try:
        with open('print_log.json', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
    except:
        pass
    
    # Вернуть последние 10
    return jsonify(history[-10:])

# ============================================================================
# ПРИМЕР 8: Кастомный формат чека с шапкой и подвалом
# ============================================================================

def format_receipt_custom(weather_data, header='', footer='', tape_width_mm=60):
    """
    Чек с пользовательской шапкой и подвалом
    """
    width = 48  # для 60мм
    
    lines = []
    
    # Шапка
    if header:
        lines.append(header.center(width))
        lines.append("=" * width)
    
    # Стандартное содержимое
    lines.append("ПОГОДА".center(width))
    lines.append(f"Город: {weather_data.get('city', 'Unknown')}")
    lines.append(f"Темп: {weather_data.get('temp')}°C")
    lines.append("")
    
    # Подвал
    if footer:
        lines.append("=" * width)
        lines.append(footer.center(width))
    
    return "\n".join(lines)

# Использование:
"""
text = format_receipt_custom(
    weather_data,
    header="КАФЕ 'УЮТНАЯ ЧАШКА'",
    footer="Спасибо, приходите еще!"
)
"""

# ============================================================================
# ПРИМЕР 9: Интеграция с Home Assistant через REST API
# ============================================================================

def send_to_home_assistant(weather_data, ha_url, ha_token):
    """
    Отправить данные погоды в Home Assistant
    """
    import requests
    
    headers = {
        'Authorization': f'Bearer {ha_token}',
        'Content-Type': 'application/json'
    }
    
    # Обновить entities в Home Assistant
    for sensor_name, value in [
        ('sensor.weather_temperature', weather_data['temp']),
        ('sensor.weather_humidity', weather_data['humidity']),
        ('sensor.weather_wind_speed', weather_data['wind_speed'])
    ]:
        url = f"{ha_url}/api/states/{sensor_name}"
        payload = {
            'state': str(value),
            'attributes': {'unit_of_measurement': 'unit'}
        }
        try:
            requests.post(url, json=payload, headers=headers, timeout=5)
        except:
            pass

# ============================================================================
# ПРИМЕР 10: Тестирование печати без реального принтера
# ============================================================================

def print_receipt_to_file(text, filename='output.txt'):
    """
    Печать в файл вместо принтера (для тестирования)
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except:
        return False

# Использование для отладки:
"""
# В weather_bot.py временно изменить:
# success = print_receipt(receipt_text, printer_name)
# На:
# success = print_receipt_to_file(receipt_text, 'test_receipt.txt')
"""

print("""
╔════════════════════════════════════════════════════════════════════╗
║              ПРИМЕРЫ РАСШИРЕНИЯ ФУНКЦИОНАЛА                       ║
╚════════════════════════════════════════════════════════════════════╝

Это файл с примерами кода для расширения приложения.

Примеры:
  1. Прогноз на несколько дней
  2. Поддержка других размеров лент
  3. Несколько городов на одном чеке
  4. Кастомные ASCII иконки
  5. Логирование всех печатей
  6. Уведомления в Telegram
  7. История печатей в веб-интерфейсе
  8. Кастомная шапка и подвал чека
  9. Интеграция с Home Assistant
  10. Тестирование в файл

Для использования примера:
  1. Скопировать код
  2. Адаптировать для своего случая
  3. Добавить в нужный модуль
  4. Пересохранить конфиг
  5. Протестировать
""")
