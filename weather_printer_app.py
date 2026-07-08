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
    "receipt_width_chars": 24,
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
    """Get list of Windows printers"""
    try:
        import win32print
        printers = []
        for printer in win32print.EnumPrinters(2):
            printers.append(printer[2])
        return printers
    except:
        return []

def is_weather_bot_running():
    """Check if background service is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'weather_bot.py' in ' '.join(cmdline):
                return True
        except:
            pass
    return False

def start_weather_bot():
    """Start background service"""
    if not is_weather_bot_running():
        subprocess.Popen(['python', 'weather_bot.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(2)
        return is_weather_bot_running()
    return True

def stop_weather_bot():
    """Stop background service"""
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Receipt Printer</title>
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
        input[type="text"], input[type="time"], select, input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 8px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="time"]:focus, select:focus, input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
            background: #f8f9ff;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>☀ Weather Receipt</h1>
        
        <div id="status" class="status stopped">
            Service: <strong id="status-text">STOPPED</strong>
        </div>

        <div class="section">
            <label>OpenWeatherMap API Key</label>
            <input type="text" id="api_key" placeholder="sk-xxxxxxxxxxxxx">
            <div class="info-text">Get at openweathermap.org</div>
        </div>

        <div class="section">
            <label>City</label>
            <input type="text" id="city" placeholder="Chișinău">
        </div>

        <div class="section">
            <label>Printer</label>
            <select id="printer">
                <option value="">-- Select printer --</option>
            </select>
            <div class="info-text">Available Windows printers</div>
        </div>

        <div class="section">
            <label>Tape Width (mm)</label>
            <input type="number" id="tape_width" min="32" max="80" value="60">
        </div>

        <div class="section">
            <label>Receipt Width (characters)</label>
            <input type="number" id="receipt_width" min="16" max="80" value="24">
            <div class="info-text">Characters per line (16-80)</div>
        </div>

        <div class="section">
            <h3 style="margin-bottom: 15px; font-size: 16px;">📅 Schedule</h3>
            <label>
                <input type="checkbox" id="schedule_enabled">
                Enable auto print
            </label>
            
            <label style="margin-top: 15px;">Print Time</label>
            <input type="time" id="schedule_time" value="09:00">
            
            <label style="margin-top: 15px;">Days of Week</label>
            <div class="checkbox-group">
                <label><input type="checkbox" name="day" value="MON"> Mon</label>
                <label><input type="checkbox" name="day" value="TUE"> Tue</label>
                <label><input type="checkbox" name="day" value="WED"> Wed</label>
                <label><input type="checkbox" name="day" value="THU"> Thu</label>
                <label><input type="checkbox" name="day" value="FRI"> Fri</label>
                <label><input type="checkbox" name="day" value="SAT"> Sat</label>
                <label><input type="checkbox" name="day" value="SUN"> Sun</label>
            </div>
        </div>

        <div class="button-group">
            <button class="btn-primary" onclick="printNow()">🖨 Print Now</button>
            <button class="btn-danger" onclick="refreshPrinters()">🔄 Refresh</button>
        </div>

        <div class="button-group" style="grid-template-columns: 1fr;">
            <button class="btn-success" onclick="saveAndStart()">💾 Save & Start</button>
        </div>
    </div>

    <script>
        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                const config = await response.json();
                
                document.getElementById('api_key').value = config.openweather_api_key;
                document.getElementById('city').value = config.city;
                document.getElementById('printer').value = config.printer_name;
                document.getElementById('tape_width').value = config.tape_width_mm;
                document.getElementById('receipt_width').value = config.receipt_width_chars || 24;
                
                document.getElementById('schedule_enabled').checked = config.schedule.enabled;
                document.getElementById('schedule_time').value = config.schedule.time;
                
                config.schedule.days.forEach(day => {
                    document.querySelector(`input[name="day"][value="${day}"]`).checked = true;
                });
            } catch (err) {
                console.error('Error loading config:', err);
            }
        }

        async function refreshPrinters() {
            try {
                const response = await fetch('/api/printers');
                const printers = await response.json();
                const select = document.getElementById('printer');
                const current = select.value;
                
                select.innerHTML = '<option value="">-- Select printer --</option>';
                printers.forEach(printer => {
                    const option = document.createElement('option');
                    option.value = printer;
                    option.textContent = printer;
                    select.appendChild(option);
                });
                
                select.value = current;
            } catch (err) {
                console.error('Error loading printers:', err);
                alert('Error getting printer list');
            }
        }

        async function saveAndStart() {
            const days = Array.from(document.querySelectorAll('input[name="day"]:checked'))
                .map(el => el.value);
            
            const config = {
                openweather_api_key: document.getElementById('api_key').value,
                city: document.getElementById('city').value,
                printer_name: document.getElementById('printer').value,
                tape_width_mm: parseInt(document.getElementById('tape_width').value),
                receipt_width_chars: parseInt(document.getElementById('receipt_width').value),
                schedule: {
                    enabled: document.getElementById('schedule_enabled').checked,
                    time: document.getElementById('schedule_time').value,
                    days: days
                }
            };

            if (!config.openweather_api_key) {
                alert('Enter OpenWeatherMap API key!');
                return;
            }
            if (!config.city) {
                alert('Enter city!');
                return;
            }
            if (!config.printer_name) {
                alert('Select printer!');
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
                    alert('Config saved!');
                    updateStatus();
                } else {
                    alert('Error saving config');
                }
            } catch (err) {
                console.error('Error:', err);
                alert('Error saving config');
            }
        }

        async function printNow() {
            try {
                const response = await fetch('/api/print-now', { method: 'POST' });
                const result = await response.json();
                alert(result.message);
            } catch (err) {
                console.error('Print error:', err);
                alert('Print error');
            }
        }

        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                const statusEl = document.getElementById('status');
                const statusText = document.getElementById('status-text');
                
                if (data.running) {
                    statusEl.className = 'status running';
                    statusText.textContent = 'RUNNING ✓';
                } else {
                    statusEl.className = 'status stopped';
                    statusText.textContent = 'STOPPED';
                }
            } catch (err) {
                console.error('Status error:', err);
            }
        }

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
        "message": "Config saved and service started" if running else "Config saved"
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
            return jsonify({"message": "Printing..."})
        else:
            return jsonify({"message": "Print error"}), 500
    except:
        return jsonify({"message": "Service not responding"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')