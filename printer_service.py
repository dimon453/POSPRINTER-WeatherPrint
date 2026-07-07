"""
Модуль для печати на чековый принтер через ESC/POS
Работает с USB принтерами типа 80mm Series Printer
"""
import subprocess
import tempfile
import os
import sys
import time

# Попробуем использовать python-escpos если установлена
try:
    from escpos.printer import Usb
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False

def print_receipt(text, printer_name):
    """
    Печать текста на чековый принтер
    
    Args:
        text: Строка текста для печати
        printer_name: Имя принтера в системе (80mm Series Printer)
    
    Returns:
        bool: True если успешно, False если ошибка
    """
    
    try:
        # Метод 1: Попробовать ESC/POS через python-escpos
        if ESCPOS_AVAILABLE:
            result = print_via_escpos(text)
            if result:
                return True
        
        # Метод 2: Попробовать через Notepad (работает из теста)
        result = print_via_notepad(text)
        if result:
            return True
        
        # Метод 3: Отправить через print команду
        result = print_via_print_command(text, printer_name)
        if result:
            return True
        
        print("✗ Ни один из способов печати не сработал")
        return False
    
    except Exception as e:
        print(f"Исключение при печати: {e}")
        return False


def print_via_escpos(text):
    """
    Печать через python-escpos (ESC/POS команды)
    Это правильный способ для чековых принтеров
    """
    try:
        if not ESCPOS_AVAILABLE:
            return False
        
        # USB принтер (80mm Series Printer)
        # Попробуем найти по USB ID (Эти значения типичны для чековых принтеров)
        try:
            # Стандартные USB ID для чековых принтеров
            printer = Usb(0x0416, 0x5011)  # Xprinter
        except:
            try:
                printer = Usb(0x0483, 0x0201)  # ZJiang
            except:
                try:
                    printer = Usb(0x04b8, 0x0202)  # Epson
                except:
                    return False
        
        # Обработать текст
        lines = text.split('\n')
        
        for line in lines:
            # Отправить строку
            if line.strip():
                printer.text(line + '\n')
            else:
                printer.text('\n')
        
        # Завершить печать
        printer.cut()
        printer.close()
        
        print("✓ Печать через ESC/POS успешна")
        return True
    
    except Exception as e:
        print(f"Ошибка ESC/POS: {e}")
        return False


def print_via_notepad(text):
    """
    Печать через Notepad (раз из Notepad печатает, используем это)
    Создаем файл и открываем его в Notepad с параметром печати
    """
    try:
        # Создать временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_file = f.name
        
        try:
            # Notepad с параметром печати на принтер по умолчанию
            cmd = f'notepad /pt "{temp_file}" "80mm Series Printer"'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Notepad /pt работает тихо, проверяем return code
            if result.returncode == 0:
                print(f"✓ Печать через Notepad успешна")
                return True
            else:
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
        print(f"Ошибка Notepad печати: {e}")
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
            
            if result.returncode == 0 and "Unable" not in result.stdout:
                print(f"✓ Печать через print команду успешна")
                return True
            else:
                print(f"⚠ Print команда: {result.stdout}")
                return False
        
        finally:
            time.sleep(0.5)
            if os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    except Exception as e:
        print(f"Ошибка print команды: {e}")
        return False


def get_printer_status(printer_name):
    """
    Получить статус принтера
    """
    try:
        import subprocess
        
        cmd = f'wmic printer where name="{printer_name}" get printerstatus'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        return {
            'name': printer_name,
            'status': 'online' if result.returncode == 0 else 'offline'
        }
    except:
        return None
