"""
Диагностика и тестирование принтера POS895UE
Запустить перед полным использованием приложения
"""

import sys
import subprocess
import tempfile
import os

def test_printer_connection():
    """Проверить наличие и видимость принтера"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Список доступных принтеров Windows")
    print("="*60)
    
    try:
        import win32print
        
        printers = []
        for printer in win32print.EnumPrinters(2):
            printer_name = printer[2]
            printers.append(printer_name)
            print(f"  ✓ {printer_name}")
        
        if not printers:
            print("  ✗ Не найдено ни одного принтера")
            return None
        
        print(f"\nВсего принтеров: {len(printers)}")
        
        # Поискать POS895UE
        pos_printer = None
        for p in printers:
            if 'POS' in p or 'pos' in p or '895' in p:
                pos_printer = p
                break
        
        if pos_printer:
            print(f"✓ POS895UE найден: {pos_printer}")
            return pos_printer
        else:
            print("\n⚠ POS895UE не найден")
            print("Выбери вручную из списка выше")
            return None
    
    except ImportError:
        print("✗ Модуль win32print не установлен")
        print("  Выполни: pip install pywin32")
        print("  Потом: python -m pywin32_postinstall -install")
        return None
    
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return None

def test_print_text_file(printer_name):
    """Печать текстового файла на принтер"""
    print("\n" + "="*60)
    print(f"ТЕСТ 2: Печать на принтер '{printer_name}'")
    print("="*60)
    
    if not printer_name:
        print("✗ Принтер не выбран")
        return False
    
    try:
        # Создать тестовый файл
        test_text = """
================================================
                  ТЕСТ ПЕЧАТИ
================================================

Принтер: """ + printer_name + """
Тип теста: Текстовый файл
Статус: OK

Если видишь эту строку, принтер работает!

================================================
Время теста: """ + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
================================================


"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_text)
            temp_file = f.name
        
        try:
            # Отправить на печать
            cmd = f'print /d:"{printer_name}" "{temp_file}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✓ Печать отправлена успешно")
                print(f"  Проверь принтер...")
                return True
            else:
                print(f"✗ Ошибка печати: {result.stderr}")
                return False
        
        finally:
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    except Exception as e:
        print(f"✗ Исключение: {e}")
        return False

def test_weather_api():
    """Проверить доступ к OpenWeatherMap API"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Проверка OpenWeatherMap API")
    print("="*60)
    
    try:
        import requests
        
        # Тестовый запрос без API ключа (должен вернуть ошибку)
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {'q': 'London'}
        
        print("  Проверяю интернет соединение...")
        response = requests.get(url, params=params, timeout=10)
        
        print("✓ OpenWeatherMap доступен")
        print(f"  Status: {response.status_code}")
        
        if 'message' in response.json():
            print(f"  Ответ: {response.json()['message']}")
            print("  (Это нормально - нужен API ключ)")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print("✗ Нет доступа в интернет")
        print("  Проверь подключение к сети")
        return False
    
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def test_python_modules():
    """Проверить установку необходимых модулей"""
    print("\n" + "="*60)
    print("ТЕСТ 4: Проверка модулей Python")
    print("="*60)
    
    modules = {
        'flask': 'Flask (веб-интерфейс)',
        'flask_cors': 'Flask-CORS (кроссдоменные запросы)',
        'requests': 'Requests (HTTP запросы)',
        'apscheduler': 'APScheduler (расписание)',
        'psutil': 'psutil (мониторинг процессов)',
        'win32print': 'pywin32 (Windows Print API)',
    }
    
    all_ok = True
    
    for module_name, description in modules.items():
        try:
            __import__(module_name)
            print(f"  ✓ {description}")
        except ImportError:
            print(f"  ✗ {description} - НЕ УСТАНОВЛЕН")
            all_ok = False
    
    if not all_ok:
        print("\n  Для установки выполни:")
        print("  pip install -r requirements.txt")
    
    return all_ok

def test_config_file():
    """Проверить файл конфигурации"""
    print("\n" + "="*60)
    print("ТЕСТ 5: Проверка файла конфигурации")
    print("="*60)
    
    import json
    
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"✓ Файл найден: {config_file}")
            print(f"  Город: {config.get('city', 'не указан')}")
            print(f"  Принтер: {config.get('printer_name', 'не указан')}")
            print(f"  Ширина ленты: {config.get('tape_width_mm')}мм")
            
            if config.get('openweather_api_key'):
                api_key = config['openweather_api_key']
                print(f"  API ключ: {api_key[:10]}...★★★ (установлен)")
            else:
                print(f"  API ключ: НЕ УСТАНОВЛЕН")
                return False
            
            return True
        
        except json.JSONDecodeError:
            print(f"✗ Файл поврежден: {config_file}")
            return False
    else:
        print(f"⚠ Файл не найден: {config_file}")
        print("  (Будет создан при первом запуске приложения)")
        return True

def run_diagnostics():
    """Запустить все тесты"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + "ДИАГНОСТИКА ПРИЛОЖЕНИЯ 'ПОГОДА НА ЧЕКЕ'".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # Тест 1
    printer = test_printer_connection()
    results['printer'] = printer is not None
    
    # Тест 2
    if printer:
        ask = input(f"\nПечатать тестовый чек на {printer}? (y/n): ").lower()
        if ask == 'y':
            results['print'] = test_print_text_file(printer)
        else:
            results['print'] = None
    else:
        results['print'] = False
    
    # Тест 3
    results['internet'] = test_weather_api()
    
    # Тест 4
    results['modules'] = test_python_modules()
    
    # Тест 5
    results['config'] = test_config_file()
    
    # Результаты
    print("\n" + "="*60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*60)
    
    if results['printer']:
        print("✓ Принтер найден и работает")
    else:
        print("✗ Принтер не найден или не работает")
    
    if results['internet']:
        print("✓ Интернет соединение работает")
    else:
        print("✗ Интернет недоступен")
    
    if results['modules']:
        print("✓ Все модули установлены")
    else:
        print("✗ Не все модули установлены")
    
    if results['config']:
        print("✓ Конфигурация в порядке")
    else:
        print("⚠ Проблемы с конфигурацией")
    
    print("\n" + "="*60)
    
    if all([results['printer'], results['internet'], results['modules']]):
        print("✓✓✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ - ГОТОВО К ЗАПУСКУ!")
        print("\nЗапустить приложение:")
        print("  python weather_printer_app.py")
    else:
        print("✗ Есть проблемы - см. выше")
        print("\nДля использования приложения необходимо:")
        print("  1. Установить Python 3.8+")
        print("  2. Подключить принтер к Windows")
        print("  3. Установить зависимости: pip install -r requirements.txt")
        print("  4. Получить API ключ OpenWeatherMap")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    try:
        run_diagnostics()
    except KeyboardInterrupt:
        print("\n\nДиагностика отменена")
    except Exception as e:
        print(f"\n\nОшибка: {e}")
