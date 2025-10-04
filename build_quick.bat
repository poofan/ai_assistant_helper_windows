@echo off
REM ========================================
REM    AI Chat Assistant - Quick Build
REM    Быстрая сборка (если venv уже настроен)
REM ========================================

echo.
echo 🚀 Быстрая сборка AI Chat Assistant...
echo.

REM Set UTF-8 encoding
chcp 65001 >nul 2>&1

REM Activate virtual environment
if not exist "venv" (
    echo ❌ Виртуальное окружение не найдено!
    echo Запустите build_auto_screenshots.bat для полной настройки
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo ✅ Виртуальное окружение активировано

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo ✅ Предыдущие сборки очищены

REM Create version info
echo # UTF-8 > version_info.txt
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

echo 🔨 Создание исполняемого файла...
pyinstaller --onefile --windowed --name "AI_Chat_Assistant" --icon "images\logo.ico" --version-file "version_info.txt" --add-data "config.ini;." --add-data "data;data" --add-data "images;images" main.py

if %errorlevel% neq 0 (
    echo ❌ Ошибка создания исполняемого файла
    pause
    exit /b 1
)

REM Create ZIP
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set ZIP_NAME=AI_Chat_Assistant_%TIMESTAMP%.zip

powershell "Compress-Archive -Path 'dist\AI_Chat_Assistant.exe' -DestinationPath '%ZIP_NAME%' -Force"

echo.
echo ✅ Сборка завершена: %ZIP_NAME%
echo.

REM Cleanup
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "version_info.txt" del "version_info.txt"
if exist "AI_Chat_Assistant.spec" del "AI_Chat_Assistant.spec"

echo 🎉 Готово!
pause
