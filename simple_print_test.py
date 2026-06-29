"""
Простой тест печати - проверка что реально печатается
"""
import subprocess
import tempfile
import os
import time

print("\n" + "="*60)
print("ПРОСТОЙ ТЕСТ ПЕЧАТИ")
print("="*60)

printer = "80mm Series Printer"

# Создать файл с текстом
test_text = """
================================================
TEST PRINT
================================================
Если вы видите этот текст - печать работает!
Дата: """ + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
================================================

"""

print(f"\n1. Создаю файл...")
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
    f.write(test_text)
    temp_file = f.name

print(f"   Файл: {temp_file}")
print(f"   Размер: {os.path.getsize(temp_file)} байт")

print(f"\n2. Отправляю на печать на '{printer}'...")
cmd = f'print /d:"{printer}" "{temp_file}"'
print(f"   Команда: {cmd}")

result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

print(f"\n3. Результат:")
print(f"   Return code: {result.returncode}")
print(f"   STDOUT: {result.stdout}")
print(f"   STDERR: {result.stderr}")

if result.returncode == 0:
    print(f"\n✓ Команда выполнена успешно!")
    print(f"✓ На принтере должна быть задача печати")
else:
    print(f"\n✗ Команда вернула ошибку")

# Проверить очередь печати
print(f"\n4. Проверяю очередь печати...")
result = subprocess.run(
    f'wmic printjob list brief',
    shell=True,
    capture_output=True,
    text=True,
    timeout=10
)
print("   Задачи в очереди:")
print(result.stdout if result.stdout else "   (нет задач)")

print(f"\n5. Статус принтера...")
result = subprocess.run(
    f'wmic printer where name="{printer}" get name,printerstatus',
    shell=True,
    capture_output=True,
    text=True,
    timeout=10
)
print(result.stdout)

# Оставить файл для проверки
print(f"\n6. Тестовый файл оставлен: {temp_file}")
print(f"   (Можешь открыть его вручную и напечатать)")

print("\n" + "="*60)
print("ДАЛЬШЕ:")
print("="*60)
print("1. Погляди на принтер - появилась ли задача печати?")
print("2. Проверь очередь печати в Windows")
print("3. Если принтер молчит - может быть зависла очередь:")
print("   net stop spooler")
print("   net start spooler")
print("="*60 + "\n")

# Удалить файл
time.sleep(1)
try:
    os.unlink(temp_file)
except:
    pass
