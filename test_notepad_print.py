"""
Тест печати через Notepad /pt (молчаливая печать)
"""
import subprocess
import tempfile
import os
import time

print("\n" + "="*60)
print("ТЕСТ ПЕЧАТИ ЧЕРЕЗ NOTEPAD")
print("="*60)

printer = "80mm Series Printer"

# Создать тестовый файл
test_text = """
================================================
             ТЕСТ ПЕЧАТИ NOTEPAD
================================================
Если вы видите этот текст - печать работает!

Дата: """ + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

================================================
                  ГОТОВО!
================================================


"""

print(f"\n1. Создаю файл...")
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
    f.write(test_text)
    temp_file = f.name

print(f"   Файл: {temp_file}")

print(f"\n2. Отправляю на печать через Notepad на '{printer}'...")
cmd = f'notepad /pt "{temp_file}" "{printer}"'
print(f"   Команда: {cmd}")

result = subprocess.run(
    cmd,
    shell=True,
    capture_output=True,
    text=True,
    timeout=30
)

print(f"\n3. Результат:")
print(f"   Return code: {result.returncode}")
if result.stdout:
    print(f"   STDOUT: {result.stdout}")
if result.stderr:
    print(f"   STDERR: {result.stderr}")

if result.returncode == 0:
    print(f"\n✓✓✓ УСПЕХ! Печать отправлена!")
    print(f"    Проверь принтер - должна быть задача печати!")
else:
    print(f"\n✗ Ошибка печати")

print(f"\n" + "="*60)

# Удалить файл
time.sleep(1)
try:
    os.unlink(temp_file)
    print("✓ Временный файл удален")
except:
    pass

print("="*60 + "\n")
