@echo off
echo ========================================
echo    AI Chat Assistant - Installer
echo    Версия с автоматическими скриншотами
echo ========================================
echo.
echo Создание ярлыка на рабочем столе...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\AI Chat Assistant.lnk'); $Shortcut.TargetPath = '%%~dp0AI_Chat_Assistant.exe'; $Shortcut.IconLocation = '%%~dp0AI_Chat_Assistant.exe'; $Shortcut.Description = 'AI Chat Assistant - Smart chatbot with auto screenshots'; $Shortcut.Save()"
echo Ярлык создан на рабочем столе!
echo.
echo Теперь вы можете запустить AI Chat Assistant с рабочего стола.
echo.
echo НОВАЯ ФУНКЦИЯ: Автоматические скриншоты
echo - Нажмите Ctrl+Shift+S для включения/выключения
echo - Настраивается интервал в настройках скриншота
echo.
pause
