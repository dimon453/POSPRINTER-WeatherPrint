"""
Фоновый сервис печати погоды
Запускается как отдельный процесс
"""
import json
import os
import requests
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, jsonify
import logging

# Отключить логи
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Импортируем модули
from weather_service import get_weather
from receipt_formatter import format_receipt
from printer_service import print_receipt

app = Flask(__name__)
scheduler = BackgroundScheduler()
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def print_weather():
    """Основная функция печати погоды"""
    try:
        config = load_config()
        
        api_key = config.get('openweather_api_key', '')
        city = config.get('city', 'Chișinău')
        printer_name = config.get('printer_name', '')
        tape_width = config.get('tape_width_mm', 60)
        
        if not api_key or not printer_name:
            print(f"[{datetime.now()}] Ошибка: API ключ или принтер не настроены")
            return
        
        # Получить погоду
        print(f"[{datetime.now()}] Получаю погоду для {city}...")
        weather_data = get_weather(city, api_key)
        
        if not weather_data:
            print(f"[{datetime.now()}] Ошибка получения погоды")
            return
        
        # Отформатировать чек
        print(f"[{datetime.now()}] Форматирую чек...")
        receipt_text = format_receipt(weather_data, config.get('receipt_width_chars', 24))
        
        # Напечатать
        print(f"[{datetime.now()}] Печатаю на {printer_name}...")
        success = print_receipt(receipt_text, printer_name)
        
        if success:
            print(f"[{datetime.now()}] ✓ Печать успешна")
        else:
            print(f"[{datetime.now()}] ✗ Ошибка печати")
    
    except Exception as e:
        print(f"[{datetime.now()}] Исключение: {e}")

def setup_scheduler():
    """Настроить расписание"""
    config = load_config()
    schedule = config.get('schedule', {})
    
    # Удалить старые задачи
    scheduler.remove_all_jobs()
    
    if schedule.get('enabled', False):
        time_str = schedule.get('time', '09:00')
        days_str = ','.join(schedule.get('days', ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']))
        
        # Разобрать время
        hour, minute = map(int, time_str.split(':'))
        
        # Добавить задачу
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            day_of_week=days_str
        )
        
        scheduler.add_job(
            print_weather,
            trigger=trigger,
            id='weather_print',
            replace_existing=True,
            name='Weather Print'
        )
        
        print(f"[{datetime.now()}] Расписание установлено: {time_str} по дням {days_str}")
    else:
        print(f"[{datetime.now()}] Расписание отключено")

@app.route('/print-now', methods=['POST'])
def print_now():
    """API endpoint для печати по запросу"""
    try:
        print_weather()
        return jsonify({"status": "success", "message": "Печать выполнена"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

if __name__ == '__main__':
    print("=" * 60)
    print("ФОНОВЫЙ СЕРВИС ПЕЧАТИ ПОГОДЫ")
    print("=" * 60)
    print(f"Запущен: {datetime.now()}")
    
    # Настроить расписание
    setup_scheduler()
    scheduler.start()
    
    # Запустить Flask на порту 5001
    try:
        app.run(debug=False, port=5001, host='127.0.0.1', use_reloader=False)
    except KeyboardInterrupt:
        print("\nОстановка сервиса...")
        scheduler.shutdown()
