"""
Flask веб приложение для управления печатью погоды на принтер
"""
import json
import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import subprocess
import psutil
import time
import requests

app = Flask(__name__)
CORS(app)

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "openweather_api_key": "",
    "city": "Chișinău",
    "printer_name": "",
    "tape_width_mm": 60,
    "schedule": {
        "enabled": False,
        "time": "09:00",
        "days": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def get_windows_printers():
    """Получить список принтеров Windows"""
    try:
        import win32print
        printers = []
        for printer in win32print.EnumPrinters(2):  # 2 = PRINTER_ENUM_LOCAL
            printers.append(printer[2])  # Имя принтера
        return printers
    except:
        return []

def is_weather_bot_running():
    """Проверить, запущен ли фоновый скрипт"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'weather_bot.py' in ' '.join(cmdline):
                return True
        except:
            pass
    return False

def start_weather_bot():
    """Запустить фоновый скрипт"""
    if not is_weather_bot_running():
        subprocess.Popen(['python', 'weather_bot.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(2)
        return is_weather_bot_running()
    return True

def stop_weather_bot():
    """Остановить фоновый скрипт"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'weather_bot.py' in ' '.join(cmdline):
                proc.kill()
                return True
        except:
            pass
    return False

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Погода на Чеке</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            font-size: 28px;
        }
        .section {
            margin-bottom: 25px;
            padding-bottom: 25px;
            border-bottom: 1px solid #eee;
        }
        .section:last-child { border-bottom: none; }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
            font-size: 14px;
        }
        input[type="text"], input[type="time"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 8px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="time"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
            background: #f8f9ff;
        }
        input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 15px 0;
        }
        .checkbox-group label {
            display: flex;
            align-items: center;
            margin: 0;
            cursor: pointer;
            font-weight: 500;
        }
        input[type="checkbox"] {
            margin-right: 8px;
            cursor: pointer;
            width: 18px;
            height: 18px;
        }
        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 20px;
        }
        button {
            padding: 14px 24px;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-danger {
            background: #f093fb;
            color: white;
        }
        .btn-danger:hover {
            background: #d471e8;
        }
        .btn-success {
            background: #4caf50;
            color: white;
            grid-column: span 2;
        }
        .btn-success:hover {
            background: #45a049;
        }
        .status {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 600;
            text-align: center;
        }
        .status.running {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.stopped {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info-text {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        .loading { opacity: 0.5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>☀️ Погода на Чеке</h1>
        
        <div id="status" class="status stopped">
            Фоновый сервис: <strong id="status-text">ОСТАНОВЛЕН</strong>
        </div>

        <div class="section">
            <label>API ключ OpenWeatherMap</label>
            <input type="text" id="api_key" placeholder="sk-xxxxxxxxxxxxx">
            <div class="info-text">Получить на openweathermap.org</div>
        </div>

        <div class="section">
            <label>Город</label>
            <input type="text" id="city" placeholder="Chișinău">
        </div>

        <div class="section">
            <label>Принтер</label>
            <select id="printer">
                <option value="">-- Выбери принтер --</option>
            </select>
            <div class="info-text">Доступные принтеры Windows</div>
        </div>

        <div class="section">
            <label>Ширина ленты (мм)</label>
            <input type="number" id="tape_width" min="32" max="80" value="60">
        </div>

        <div class="section">
            <h3 style="margin-bottom: 15px; font-size: 16px;">📅 Расписание</h3>
            <label>
                <input type="checkbox" id="schedule_enabled">
                Включить автоматическую печать
            </label>
            
            <label style="margin-top: 15px;">Время печати</label>
            <input type="time" id="schedule_time" value="09:00">
            
            <label style="margin-top: 15px;">Дни недели</label>
            <div class="checkbox-group">
                <label><input type="checkbox" name="day" value="MON"> Пн</label>
                <label><input type="checkbox" name="day" value="TUE"> Вт</label>
                <label><input type="checkbox" name="day" value="WED"> Ср</label>
                <label><input type="checkbox" name="day" value="THU"> Чт</label>
                <label><input type="checkbox" name="day" value="FRI"> Пт</label>
                <label><input type="checkbox" name="day" value="SAT"> Сб</label>
                <label><input type="checkbox" name="day" value="SUN"> Вс</label>
            </div>
        </div>

        <div class="button-group">
            <button class="btn-primary" onclick="printNow()">🖨️ Печать Сейчас</button>
            <button class="btn-danger" onclick="refreshPrinters()">🔄 Обновить</button>
        </div>

        <div class="button-group" style="grid-template-columns: 1fr;">
            <button class="btn-success" onclick="saveAndStart()">💾 Сохранить и Запустить</button>
        </div>
    </div>

    <script>
        // Загрузить конфиг при открытии страницы
        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                const config = await response.json();
                
                document.getElementById('api_key').value = config.openweather_api_key;
                document.getElementById('city').value = config.city;
                document.getElementById('printer').value = config.printer_name;
                document.getElementById('tape_width').value = config.tape_width_mm;
                
                document.getElementById('schedule_enabled').checked = config.schedule.enabled;
                document.getElementById('schedule_time').value = config.schedule.time;
                
                config.schedule.days.forEach(day => {
                    document.querySelector(`input[name="day"][value="${day}"]`).checked = true;
                });
            } catch (err) {
                console.error('Ошибка загрузки конфига:', err);
            }
        }

        // Загрузить список принтеров
        async function refreshPrinters() {
            try {
                const response = await fetch('/api/printers');
                const printers = await response.json();
                const select = document.getElementById('printer');
                const current = select.value;
                
                select.innerHTML = '<option value="">-- Выбери принтер --</option>';
                printers.forEach(printer => {
                    const option = document.createElement('option');
                    option.value = printer;
                    option.textContent = printer;
                    select.appendChild(option);
                });
                
                select.value = current;
            } catch (err) {
                console.error('Ошибка загрузки принтеров:', err);
                alert('Ошибка получения списка принтеров');
            }
        }

        // Сохранить конфиг и запустить сервис
        async function saveAndStart() {
            const days = Array.from(document.querySelectorAll('input[name="day"]:checked'))
                .map(el => el.value);
            
            const config = {
                openweather_api_key: document.getElementById('api_key').value,
                city: document.getElementById('city').value,
                printer_name: document.getElementById('printer').value,
                tape_width_mm: parseInt(document.getElementById('tape_width').value),
                schedule: {
                    enabled: document.getElementById('schedule_enabled').checked,
                    time: document.getElementById('schedule_time').value,
                    days: days
                }
            };

            if (!config.openweather_api_key) {
                alert('Укажи API ключ OpenWeatherMap!');
                return;
            }
            if (!config.city) {
                alert('Укажи город!');
                return;
            }
            if (!config.printer_name) {
                alert('Выбери принтер!');
                return;
            }

            try {
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });

                if (response.ok) {
                    const result = await response.json();
                    alert('Конфиг сохранён! Сервис ' + (result.running ? 'запущен' : 'запускается'));
                    updateStatus();
                } else {
                    alert('Ошибка сохранения конфига');
                }
            } catch (err) {
                console.error('Ошибка:', err);
                alert('Ошибка сохранения конфига');
            }
        }

        // Печать сейчас
        async function printNow() {
            try {
                const response = await fetch('/api/print-now', { method: 'POST' });
                const result = await response.json();
                alert(result.message);
            } catch (err) {
                console.error('Ошибка печати:', err);
                alert('Ошибка печати');
            }
        }

        // Обновить статус сервиса
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                const statusEl = document.getElementById('status');
                const statusText = document.getElementById('status-text');
                
                if (data.running) {
                    statusEl.className = 'status running';
                    statusText.textContent = 'ЗАПУЩЕН ✓';
                } else {
                    statusEl.className = 'status stopped';
                    statusText.textContent = 'ОСТАНОВЛЕН';
                }
            } catch (err) {
                console.error('Ошибка статуса:', err);
            }
        }

        // Инициализация
        loadConfig();
        refreshPrinters();
        updateStatus();
        setInterval(updateStatus, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(load_config())

@app.route('/api/config', methods=['POST'])
def save_and_start_config():
    config = request.json
    save_config(config)
    running = start_weather_bot()
    return jsonify({
        "saved": True,
        "running": running,
        "message": "Конфиг сохранён и сервис запущен" if running else "Конфиг сохранён"
    })

@app.route('/api/printers', methods=['GET'])
def get_printers():
    return jsonify(get_windows_printers())

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({"running": is_weather_bot_running()})

@app.route('/api/print-now', methods=['POST'])
def print_now():
    try:
        response = requests.post('http://localhost:5001/print-now', timeout=5)
        if response.ok:
            return jsonify({"message": "Печать запущена"})
        else:
            return jsonify({"message": "Ошибка печати"}), 500
    except:
        return jsonify({"message": "Фоновый сервис не отвечает"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')
