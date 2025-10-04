@echo off
REM ========================================
REM    AI Chat Assistant - Auto Screenshots Build
REM    Сборка с автоматическими скриншотами
REM ========================================

echo.
echo ========================================
echo    Создание сборки AI Chat Assistant
echo    с автоматическими скриншотами
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

echo [1/8] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден! Установите Python 3.12+
    pause
    exit /b 1
)
echo ✅ Python найден

echo.
echo [2/8] Активация виртуального окружения...
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Ошибка активации виртуального окружения
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение активировано

echo.
echo [3/8] Установка PyInstaller...
pip install pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки PyInstaller
    pause
    exit /b 1
)
echo ✅ PyInstaller установлен

echo.
echo [4/8] Установка зависимостей...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)
echo ✅ Зависимости установлены

echo.
echo [5/8] Создание version_info.txt...
echo # UTF-8 > version_info.txt
echo. >> version_info.txt
echo VSVersionInfo( >> version_info.txt
echo   ffi=FixedFileInfo( >> version_info.txt
echo     filevers=(1, 0, 0, 0), >> version_info.txt
echo     prodvers=(1, 0, 0, 0), >> version_info.txt
echo     mask=0x3f, >> version_info.txt
echo     flags=0x0, >> version_info.txt
echo     OS=0x40004, >> version_info.txt
echo     fileType=0x1, >> version_info.txt
echo     subtype=0x0, >> version_info.txt
echo     date=(0, 0) >> version_info.txt
echo   ), >> version_info.txt
echo   kids=[ >> version_info.txt
echo     StringFileInfo( >> version_info.txt
echo       [ >> version_info.txt
echo         StringTable( >> version_info.txt
echo           u'040904B0', >> version_info.txt
echo           [StringStruct(u'CompanyName', u'AI Chat Assistant'), >> version_info.txt
echo            StringStruct(u'FileDescription', u'AI Chat Assistant - Smart chatbot with auto screenshots'), >> version_info.txt
echo            StringStruct(u'FileVersion', u'1.0.0.0'), >> version_info.txt
echo            StringStruct(u'InternalName', u'AI_Chat_Assistant'), >> version_info.txt
echo            StringStruct(u'LegalCopyright', u'Copyright (C) 2025'), >> version_info.txt
echo            StringStruct(u'OriginalFilename', u'AI_Chat_Assistant.exe'), >> version_info.txt
echo            StringStruct(u'ProductName', u'AI Chat Assistant'), >> version_info.txt
echo            StringStruct(u'ProductVersion', u'1.0.0.0')]) >> version_info.txt
echo       ] >> version_info.txt
echo     ), >> version_info.txt
echo     VarFileInfo([VarStruct(u'Translation', [1033, 1200])]) >> version_info.txt
echo   ] >> version_info.txt
echo ) >> version_info.txt
echo ✅ version_info.txt создан

echo.
echo [6/8] Очистка предыдущих сборок...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "AI_Chat_Assistant.spec" del "AI_Chat_Assistant.spec"
echo ✅ Предыдущие сборки очищены

echo.
echo [7/8] Создание исполняемого файла...
echo 🔨 Это может занять несколько минут...
pyinstaller --onefile --windowed --name "AI_Chat_Assistant" --icon "images\logo.ico" --version-file "version_info.txt" --add-data "config.ini;." --add-data "data;data" --add-data "images;images" main.py

if %errorlevel% neq 0 (
    echo ❌ Ошибка создания исполняемого файла
    pause
    exit /b 1
)
echo ✅ Исполняемый файл создан

echo.
echo [8/8] Создание ZIP архива...
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set ZIP_NAME=AI_Chat_Assistant_Auto_Screenshots_%TIMESTAMP%.zip

powershell "Compress-Archive -Path 'dist\AI_Chat_Assistant.exe' -DestinationPath '%ZIP_NAME%' -Force"

if %errorlevel% neq 0 (
    echo ❌ Ошибка создания ZIP архива
    pause
    exit /b 1
)

echo.
echo ========================================
echo    ✅ СБОРКА ЗАВЕРШЕНА УСПЕШНО!
echo ========================================
echo.
echo 📦 Создан файл: %ZIP_NAME%
echo 📁 Размер: 
for %%A in ("%ZIP_NAME%") do echo    %%~zA байт
echo.
echo 🚀 Возможности:
echo    • Автоматические скриншоты (Ctrl+Shift+S)
echo    • Современный дизайн чата
echo    • Гибкая система координат
echo    • Анализ изображений
echo.
echo 📋 Инструкции:
echo    1. Распакуйте архив
echo    2. Запустите AI_Chat_Assistant.exe
echo    3. Нажмите Ctrl+Shift+S для автоскриншотов
echo.
echo 🧹 Очистка временных файлов...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "version_info.txt" del "version_info.txt"
if exist "AI_Chat_Assistant.spec" del "AI_Chat_Assistant.spec"
echo ✅ Временные файлы очищены

echo.
echo Готово! 🎉
pause
