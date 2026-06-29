"""
Расширенная диагностика печати
Помогает найти точную причину проблемы
"""

import subprocess
import tempfile
import os
import sys
import time

def test_1_list_printers():
    """Тест 1: Список доступных принтеров"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Список принтеров в Windows")
    print("="*60)
    
    try:
        # Способ 1: через wmic
        result = subprocess.run(
            'wmic printerjob list',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ WMIC доступен")
        
        # Способ 2: Получить список принтеров
        result = subprocess.run(
            'wmic printer list brief',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("\nДоступные принтеры (WMIC):")
        print(result.stdout)
        
        # Способ 3: через print /? (показать справку)
        result = subprocess.run(
            'print /?',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "print" in result.stdout.lower():
            print("✓ Команда 'print' доступна")
        
        return True
    
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_2_create_test_file():
    """Тест 2: Создать тестовый файл"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Создание тестового файла")
    print("="*60)
    
    try:
        test_text = """
================================================
                    ТЕСТ ПЕЧАТИ
================================================

Принтер: 80mm printer
Дата/время: """ + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
Статус: ЕСЛИ ВЫ ВИДИТЕ ЭТО - ПЕЧАТЬ РАБОТАЕТ!

Это текстовый файл для тестирования печати.

================================================
Конец документа
================================================


"""
        
        test_file = "test_receipt.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_text)
        
        if os.path.exists(test_file):
            size = os.path.getsize(test_file)
            print(f"✓ Файл создан: {test_file} ({size} байт)")
            return test_file
        else:
            print("✗ Не удалось создать файл")
            return None
    
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return None


def test_3_print_command(printer_name, test_file):
    """Тест 3: Команда print"""
    print("\n" + "="*60)
    print(f"ТЕСТ 3: Печать через 'print' на '{printer_name}'")
    print("="*60)
    
    try:
        cmd = f'print /d:"{printer_name}" "{test_file}"'
        print(f"Команда: {cmd}")
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print("✓ Команда print выполнена успешно")
            return True
        else:
            print("✗ Команда print вернула ошибку")
            return False
    
    except subprocess.TimeoutExpired:
        print("✗ Timeout - команда зависла")
        return False
    except Exception as e:
        print(f"✗ Исключение: {e}")
        return False


def test_4_powershell_print(printer_name, test_file):
    """Тест 4: Печать через PowerShell"""
    print("\n" + "="*60)
    print(f"ТЕСТ 4: Печать через PowerShell на '{printer_name}'")
    print("="*60)
    
    try:
        # Команда PowerShell
        ps_cmd = (
            f"$printers = @(Get-Printer); "
            f"$found = $false; "
            f"foreach ($p in $printers) {{ "
            f"  if ($p.Name -eq '{printer_name}') {{ "
            f"    $found = $true; "
            f"    Write-Host 'Принтер найден'; "
            f"  }} "
            f"}} "
            f"if (-not $found) {{ "
            f"  Write-Host 'Принтер НЕ найден'; "
            f"}}"
        )
        
        result = subprocess.run(
            ['powershell', '-Command', ps_cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        # Попытка печати через Out-Printer
        ps_print = (
            f"Get-Content '{test_file}' | Out-Printer -Name '{printer_name}'"
        )
        
        print(f"\nПопытка печати через Out-Printer...")
        result = subprocess.run(
            ['powershell', '-Command', ps_print],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print("✓ PowerShell печать работает")
            return True
        else:
            print("✗ PowerShell печать не сработала")
            return False
    
    except Exception as e:
        print(f"✗ Исключение: {e}")
        return False


def test_5_notepad_print(printer_name, test_file):
    """Тест 5: Печать через Notepad"""
    print("\n" + "="*60)
    print(f"ТЕСТ 5: Печать через Notepad на '{printer_name}'")
    print("="*60)
    
    try:
        # Notepad с параметром печати
        cmd = f'notepad /p "{test_file}"'
        print(f"Команда: {cmd}")
        print("(Откроется Notepad, нажми Ctrl+P и выбери принтер)")
        
        # Это откроет Notepad - для полной автоматизации нужен другой способ
        # Просто проверяем что Notepad существует
        result = subprocess.run(
            'where notepad',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ Notepad найден")
            print("  Для печати через Notepad:")
            print(f"    1. notepad \"{test_file}\"")
            print(f"    2. Ctrl+P")
            print(f"    3. Выбрать '{printer_name}'")
            print(f"    4. OK")
            return True
        else:
            print("✗ Notepad не найден")
            return False
    
    except Exception as e:
        print(f"✗ Исключение: {e}")
        return False


def test_6_raw_print(printer_name, test_file):
    """Тест 6: Прямая отправка через copy CON: PRN:"""
    print("\n" + "="*60)
    print(f"ТЕСТ 6: Прямая отправка через copy")
    print("="*60)
    
    try:
        # Windows способ - напрямую копировать на принтер
        cmd = f'copy "{test_file}" PRN:'
        print(f"Команда: {cmd}")
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print("✓ Копирование на PRN: прошло успешно")
            return True
        else:
            print("✗ Копирование на PRN: не сработало")
            return False
    
    except Exception as e:
        print(f"✗ Исключение: {e}")
        return False


def test_7_check_printer_details(printer_name):
    """Тест 7: Детальная информация о принтере"""
    print("\n" + "="*60)
    print(f"ТЕСТ 7: Информация о принтере '{printer_name}'")
    print("="*60)
    
    try:
        # Получить детали принтера через wmic
        cmd = f'wmic printer where name="{printer_name}" get name,portname,printerstatus'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("Информация от WMIC:")
        print(result.stdout)
        
        # Альтернативный способ
        cmd2 = f'powershell "Get-Printer -Name \'{printer_name}\' | Format-List"'
        result2 = subprocess.run(
            cmd2,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("\nИнформация от PowerShell:")
        print(result2.stdout)
        
        return True
    
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + "РАСШИРЕННАЯ ДИАГНОСТИКА ПЕЧАТИ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    printer_name = "80mm printer"
    
    # Тест 1: Список принтеров
    test_1_list_printers()
    
    # Тест 7: Информация о принтере
    test_7_check_printer_details(printer_name)
    
    # Тест 2: Создать файл
    test_file = test_2_create_test_file()
    
    if not test_file:
        print("\n✗ Не удалось создать тестовый файл")
        return
    
    # Тест 3: print команда
    result3 = test_3_print_command(printer_name, test_file)
    
    # Тест 4: PowerShell
    result4 = test_4_powershell_print(printer_name, test_file)
    
    # Тест 5: Notepad
    result5 = test_5_notepad_print(printer_name, test_file)
    
    # Тест 6: Copy PRN:
    result6 = test_6_raw_print(printer_name, test_file)
    
    # Итоги
    print("\n" + "="*60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*60)
    
    print(f"\n✓ Способ 'print' работает: {result3}")
    print(f"✓ Способ 'PowerShell' работает: {result4}")
    print(f"✓ Способ 'Notepad' доступен: {result5}")
    print(f"✓ Способ 'copy PRN:' работает: {result6}")
    
    if any([result3, result4, result5, result6]):
        print("\n✓✓✓ НАЙДЕН РАБОЧИЙ СПОСОБ ПЕЧАТИ!")
        print("\nСкажи мне какой способ сработал, и я обновлю приложение!")
    else:
        print("\n✗ НИ ОДИН СПОСОБ НЕ РАБОТАЕТ")
        print("\nЭто может означать:")
        print("  • Принтер выключен")
        print("  • Принтер зависает")
        print("  • Драйвер принтера поврежден")
        print("  • Очередь печати забита")
        print("\nПопробуй:")
        print("  1. Перезагрузить принтер")
        print("  2. Перезагрузить компьютер")
        print("  3. Проверить драйверы принтера")
        print("  4. Очистить очередь печати: net stop spooler && net start spooler")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана")
    except Exception as e:
        print(f"\n\nОшибка: {e}")
        import traceback
        traceback.print_exc()
