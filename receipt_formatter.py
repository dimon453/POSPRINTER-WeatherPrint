"""
Модуль форматирования чека для печати
"""
from weather_service import get_weather_icon_ascii
from datetime import datetime

def center_text(text, width):
    """Центрировать текст"""
    return text.center(width)

def format_receipt(weather_data, tape_width_mm=60):
    """
    Отформатировать данные погоды в чек для печати
    
    Args:
        weather_data: dict с данными погоды от get_weather()
        tape_width_mm: ширина ленты в мм (32, 58, 60, 80)
    
    Returns:
        str с текстом чека, готовым к печати
    """
    
    # Примерный расчет символов для разной ширины
    width_map = {
        32: 32,
        40: 40,
        58: 46,
        60: 48,
        80: 64
    }
    
    # Выбрать ближайшую ширину
    width = width_map.get(tape_width_mm, 48)
    
    # Получить иконку погоды
    icon = get_weather_icon_ascii(weather_data.get('description', 'Clouds'))
    
    # Сформировать текст чека
    lines = []
    
    # Заголовок
    lines.append("=" * width)
    lines.append(center_text("☀ ПОГОДА ☀", width))
    lines.append("=" * width)
    lines.append("")
    
    # Город и дата/время
    city = weather_data.get('city', 'Unknown')
    timestamp = weather_data.get('timestamp', '')
    
    lines.append(center_text(city, width))
    lines.append(center_text(timestamp, width))
    lines.append("")
    
    # ASCII иконка
    for icon_line in icon:
        lines.append(center_text(icon_line, width))
    lines.append("")
    
    # Описание
    description = weather_data.get('description_ru', 'неизвестно')
    lines.append(center_text(description.title(), width))
    lines.append("")
    
    # Разделитель
    lines.append("-" * width)
    
    # Температура
    temp_current = weather_data.get('temp', 0)
    temp_min = weather_data.get('temp_min', 0)
    temp_max = weather_data.get('temp_max', 0)
    feels_like = weather_data.get('feels_like', 0)
    
    lines.append(f"Температура:  {temp_current}°C")
    lines.append(f"Мин/макс:     {temp_min}°C / {temp_max}°C")
    lines.append(f"Ощущается как: {feels_like}°C")
    lines.append("")
    
    # Влажность
    humidity = weather_data.get('humidity', 0)
    lines.append(f"Влажность:    {humidity}%")
    
    # Ветер
    wind_speed = weather_data.get('wind_speed', 0)
    lines.append(f"Ветер:        {wind_speed} м/с")
    
    lines.append("")
    lines.append("=" * width)
    lines.append(center_text("Спасибо за внимание! 🌍", width))
    lines.append("=" * width)
    lines.append("")
    
    # Добавить несколько пустых строк для отрезания
    lines.append("\n\n")
    
    return "\n".join(lines)

def format_receipt_compact(weather_data, tape_width_mm=60):
    """
    Компактный вариант чека (если место ограничено)
    """
    
    width_map = {
        32: 32,
        40: 40,
        58: 46,
        60: 48,
        80: 64
    }
    
    width = width_map.get(tape_width_mm, 48)
    
    lines = []
    
    # Короткий формат
    lines.append("=" * width)
    city = weather_data.get('city', 'Unknown')
    lines.append(center_text(f"{city} - Погода", width))
    lines.append("=" * width)
    
    temp = weather_data.get('temp', 0)
    desc = weather_data.get('description_ru', 'неизвестно')
    humidity = weather_data.get('humidity', 0)
    wind = weather_data.get('wind_speed', 0)
    feels = weather_data.get('feels_like', 0)
    
    lines.append(f"{desc.title():.<width}")
    lines.append(f"Темп: {temp}°C (ощущается {feels}°C)")
    lines.append(f"Влаж: {humidity}% | Ветер: {wind}м/с")
    lines.append("=" * width)
    lines.append("\n\n")
    
    return "\n".join(lines)

# Тестирование
if __name__ == '__main__':
    test_data = {
        'city': 'Chișinău',
        'country': 'MD',
        'description': 'Clouds',
        'description_ru': 'облачно',
        'temp': 18,
        'temp_min': 15,
        'temp_max': 22,
        'feels_like': 17,
        'humidity': 65,
        'wind_speed': 3.5,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(format_receipt(test_data, 60))
    print("\n" + "="*60 + "\n")
    print(format_receipt_compact(test_data, 60))
