"""
Receipt formatting module for printing
Dynamic width support
"""
from weather_service import get_weather_icon_ascii
from datetime import datetime

def format_receipt(weather_data, receipt_width=24):
    """
    Receipt with dynamic character width per line
    Text centered within character limit
    """
    
    # Get data
    city = weather_data.get('city', 'Unknown')[:receipt_width]
    timestamp = weather_data.get('timestamp', '')
    desc = weather_data.get('description', '?')[:receipt_width]
    temp = int(weather_data.get('temp', 0))
    temp_min = int(weather_data.get('temp_min', 0))
    temp_max = int(weather_data.get('temp_max', 0))
    feels = int(weather_data.get('feels_like', 0))
    humidity = int(weather_data.get('humidity', 0))
    wind = weather_data.get('wind_speed', 0)
    
    # Split date/time
    date_str = timestamp.split()[0] if timestamp else "2000-01-01"
    time_str = timestamp.split()[1] if len(timestamp.split()) > 1 else "00:00:00"
    
    # Get weather icon
    icon = get_weather_icon_ascii(weather_data.get('description', 'Clouds'))
    
    lines = []
    
    # Dynamic width - centered
    lines.append("=" * receipt_width)
    lines.append("WEATHER".center(receipt_width))
    lines.append("=" * receipt_width)
    lines.append("")
    lines.append(city.center(receipt_width))
    lines.append(date_str.center(receipt_width))
    lines.append(time_str.center(receipt_width))
    lines.append("")
    
    # Add ASCII art icon (trim to fit)
    for icon_line in icon:
        trimmed = icon_line.strip()[:receipt_width-2]
        lines.append(trimmed.center(receipt_width))
    lines.append("")
    
    lines.append(desc.center(receipt_width))
    lines.append("")
    lines.append("-" * receipt_width)
    lines.append("")
    lines.append(f"Temp:{temp}°".center(receipt_width))
    lines.append(f"Min:{temp_min}° Max:{temp_max}°".center(receipt_width))
    lines.append(f"Feel:{feels}°".center(receipt_width))
    lines.append("")
    lines.append(f"Humidity:{humidity}%".center(receipt_width))
    lines.append(f"Wind:{wind}m/s".center(receipt_width))
    lines.append("")
    lines.append("=" * receipt_width)
    lines.append("Thank You!".center(receipt_width))
    lines.append("=" * receipt_width)
    lines.append("")
    lines.append("")
    lines.append("")
    
    return "\n".join(lines)

def format_receipt_compact(weather_data, receipt_width=24):
    """Compact version"""
    return format_receipt(weather_data, receipt_width)

if __name__ == '__main__':
    test_data = {
        'city': 'Chisinau',
        'description': 'Clouds',
        'temp': 18,
        'temp_min': 15,
        'temp_max': 22,
        'feels_like': 17,
        'humidity': 65,
        'wind_speed': 3.5,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    receipt = format_receipt(test_data, 24)
    print(receipt)