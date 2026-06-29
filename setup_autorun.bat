@echo off
REM Скрипт для создания ярлыка автозапуска приложения на Windows
REM Запустить от администратора!

setlocal enabledelayedexpansion

REM Получить путь к текущей папке
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Создать ярлык для запуска в Startup
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Создать батник для запуска приложения
echo @echo off > "%SCRIPT_DIR%\run_weather_printer.bat"
echo cd /d "%SCRIPT_DIR%" >> "%SCRIPT_DIR%\run_weather_printer.bat"
echo python weather_printer_app.py >> "%SCRIPT_DIR%\run_weather_printer.bat"
echo pause >> "%SCRIPT_DIR%\run_weather_printer.bat"

REM Создать VBS скрипт для скрытого запуска
echo CreateObject("WScript.Shell").Run "cmd /c cd /d ""%SCRIPT_DIR%"" ^& python weather_printer_app.py", 0, False > "%SCRIPT_DIR%\run_hidden.vbs"

REM Создать ярлык в папке Startup для скрытого запуска
powershell -Command ^
"$WshShell = New-Object -ComObject WScript.Shell; ^
$shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\Weather Printer.lnk'); ^
$shortcut.TargetPath = '%SCRIPT_DIR%\run_hidden.vbs'; ^
$shortcut.WorkingDirectory = '%SCRIPT_DIR%'; ^
$shortcut.IconLocation = 'C:\Windows\System32\shell32.dll,12'; ^
$shortcut.Save()"

echo.
echo ✓ Автозапуск установлен!
echo.
echo Приложение будет запускаться при включении компьютера.
echo.
echo Для отключения автозапуска:
echo   Откройте %STARTUP_FOLDER%
echo   Удалите файл "Weather Printer.lnk"
echo.
pause
