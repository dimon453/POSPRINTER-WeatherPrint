"""
Модуль для печати на Windows принтер
Работает с POS895UE и другими принтерами через встроенные Windows команды
(БЕЗ pywin32 - полностью встроенное решение)
"""
import subprocess
import tempfile
import os
import sys
import time

def print_receipt(text, printer_name):
    """
    Печать текста на принтер
    
    Args:
        text: Строка текста для печати
        printer_name: Имя принтера в системе
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    
    try:
        # Метод 1: Попробовать через Notepad (самый надежный для обычного текста)
        result = print_via_notepad(text, printer_name)
        if result:
            return True
        
        # Метод 2: Попробовать через встроенную команду print
        result = print_via_print_command(text, printer_name)
        if result:
            return True
        
        # Метод 3: Попробовать через type и LPT1 (для чековых принтеров)
        result = print_via_lpt(text, printer_name)
        if result:
            return True
        
        print("✗ Ни один из способов печати не сработал")
        return False
    
    except Exception as e:
        print(f"Исключение при печати: {e}")
        return False


def print_via_notepad(text, printer_name):
    """
    Печать через Notepad + встроенная команда print
    Это самый надежный способ для Windows
    """
    try:
        # Создать временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_file = f.name
        
        try:
            # Попробовать несколько вариантов команды print
            commands = [
                # Вариант 1: Стандартная команда print
                f'print /d:"{printer_name}" "{temp_file}"',
                
                # Вариант 2: С явным указанием Notepad
                f'notepad /p "{temp_file}" "{printer_name}"',
                
                # Вариант 3: Через PowerShell
                f'powershell -Command "$printers = Get-Printer; '
                f'Get-Content \'{temp_file}\' | '
                f'Out-Printer -Name \'{printer_name}\'"',
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print(f"✓ Печать успешна на {printer_name}")
                        return True
                except subprocess.TimeoutExpired:
                    continue
                except Exception as e:
                    continue
            
            return False
        
        finally:
            # Удалить временный файл с задержкой
            time.sleep(1)
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    except Exception as e:
        print(f"Ошибка print_via_notepad: {e}")
        return False


def print_via_print_command(text, printer_name):
    """
    Печать через встроенную команду print
    """
    try:
        # Создать временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_file = f.name
        
        try:
            # Отправить на печать
            cmd = f'print /d:"{printer_name}" "{temp_file}"'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✓ Печать успешна на {printer_name} (print command)")
                return True
            else:
                return False
        
        finally:
            time.sleep(0.5)
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    except Exception as e:
        print(f"Ошибка print_via_print_command: {e}")
        return False


def print_via_lpt(text, printer_name):
    """
    Печать прямой отправкой на LPT порт (для чековых принтеров)
    """
    try:
        # Найти порт принтера
        import winreg
        
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Print\Printers"
        )
        
        try:
            subkey = winreg.OpenKey(key, printer_name)
            port, _ = winreg.QueryValueEx(subkey, "Port")
            winreg.CloseKey(subkey)
            winreg.CloseKey(key)
            
            # Отправить текст напрямую на порт
            with open(port, 'w', encoding='utf-8', errors='replace') as printer:
                printer.write(text)
            
            print(f"✓ Печать успешна на {printer_name} (LPT)")
            return True
        
        except:
            return False
    
    except Exception as e:
        print(f"Ошибка print_via_lpt: {e}")
        return False


def get_printer_status(printer_name):
    """
    Получить статус принтера
    """
    try:
        # Просто проверить что принтер существует
        import subprocess
        
        cmd = f'wmic printerjob where name like "%{printer_name}%" get status'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        return {
            'name': printer_name,
            'status': 'online' if result.returncode == 0 else 'offline'
        }
    except:
        return None

def print_receipt_lpr(text, printer_name):
    """
    Печать через LPR (для сетевых принтеров)
    Используется если принтер подключен по IP
    """
    try:
        # Парсим IP адрес и очередь из имени принтера
        # Формат: "IP_адрес:queue_name"
        if ':' in printer_name:
            host, queue = printer_name.split(':')
        else:
            host = printer_name
            queue = 'lp'
        
        # Создать временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_file = f.name
        
        try:
            # Отправить через LPR
            cmd = f'lpr -S {host} -P {queue} {temp_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            return result.returncode == 0
        finally:
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    except Exception as e:
        print(f"Ошибка LPR печати: {e}")
        return False

def get_printer_status(printer_name):
    """
    Получить статус принтера
    """
    try:
        import win32print
        
        handle = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(handle, 0)
        win32print.ClosePrinter(handle)
        
        return {
            'name': printer_info[1],
            'status': printer_info[9],
            'jobs': printer_info[10]
        }
    except:
        return None

# Тестирование
if __name__ == '__main__':
    # Тестовый текст
    test_text = """
================================================
                   ТЕСТ ПЕЧАТИ
================================================
Это тестовый чек для принтера
================================================
Дата: 2024-01-01
Время: 12:00:00
Статус: OK
================================================
"""
    
    print("Доступные принтеры:")
    try:
        import win32print
        for printer in win32print.EnumPrinters(2):
            print(f"  - {printer[2]}")
    except:
        print("  Не удалось получить список принтеров")
