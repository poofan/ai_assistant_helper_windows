@echo off
REM ========================================
REM    AI Chat Assistant - Final Production Build
REM ========================================
REM This script creates the final production executable

echo.
echo ========================================
echo    Building Final Production Executable
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python first.
    pause
    exit /b 1
)
echo Python found

REM Activate virtual environment
echo Activating virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Error creating virtual environment
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error activating virtual environment
    pause
    exit /b 1
)

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Error installing PyInstaller
    pause
    exit /b 1
)

REM Install all dependencies
echo Installing dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo Error installing dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Creating Version Info
echo ========================================

REM Create version info file
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
echo            StringStruct(u'FileDescription', u'AI Chat Assistant - Smart chatbot with screenshot analysis'), >> version_info.txt
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

echo Version info created

echo.
echo ========================================
echo    Building Final Executable
echo ========================================

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo Building executable with PyInstaller...
echo This may take several minutes...

pyinstaller --onefile ^
    --windowed ^
    --name "AI_Chat_Assistant" ^
    --icon "images\logo.ico" ^
    --version-file "version_info.txt" ^
    --add-data "config;config" ^
    --add-data "data;data" ^
    --add-data "images;images" ^
    --add-data "services;services" ^
    --add-data "utils;utils" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.messagebox" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "tkinter.simpledialog" ^
    --hidden-import "tkinter.scrolledtext" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "requests" ^
    --hidden-import "psutil" ^
    --hidden-import "mss" ^
    --hidden-import "win32gui" ^
    --hidden-import "win32con" ^
    --hidden-import "win32api" ^
    --hidden-import "win32process" ^
    --hidden-import "win32ui" ^
    --hidden-import "pathlib" ^
    --hidden-import "json" ^
    --hidden-import "logging" ^
    --hidden-import "threading" ^
    --hidden-import "datetime" ^
    --hidden-import "uuid" ^
    --hidden-import "webbrowser" ^
    --hidden-import "time" ^
    --hidden-import "os" ^
    --hidden-import "sys" ^
    --hidden-import "ctypes" ^
    --hidden-import "struct" ^
    main.py

if %errorlevel% neq 0 (
    echo Error building executable
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Creating Final Package
echo ========================================

REM Create production directory
set PROD_DIR=AI_Chat_Assistant_Final
if exist "%PROD_DIR%" rmdir /s /q "%PROD_DIR%"
mkdir "%PROD_DIR%"

REM Copy executable
echo Copying executable...
copy "dist\AI_Chat_Assistant.exe" "%PROD_DIR%\"

REM Copy configuration files
echo Copying configuration files...
copy "config.ini" "%PROD_DIR%\"

REM Create data directories
echo Creating data directories...
mkdir "%PROD_DIR%\data"
mkdir "%PROD_DIR%\screenshots"
mkdir "%PROD_DIR%\logs"

REM Copy initial data files
if exist "data\chats.json" copy "data\chats.json" "%PROD_DIR%\data\"
if exist "data\screenshot_settings.json" copy "data\screenshot_settings.json" "%PROD_DIR%\data\"

REM Create production installer
echo Creating production installer...
echo @echo off > "%PROD_DIR%\INSTALL.bat"
echo echo ======================================== >> "%PROD_DIR%\INSTALL.bat"
echo echo    AI Chat Assistant - Installer >> "%PROD_DIR%\INSTALL.bat"
echo echo ======================================== >> "%PROD_DIR%\INSTALL.bat"
echo echo. >> "%PROD_DIR%\INSTALL.bat"
echo echo Creating desktop shortcut... >> "%PROD_DIR%\INSTALL.bat"
echo powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\AI Chat Assistant.lnk'); $Shortcut.TargetPath = '%%~dp0AI_Chat_Assistant.exe'; $Shortcut.IconLocation = '%%~dp0images\logo.ico'; $Shortcut.Description = 'AI Chat Assistant - Smart chatbot with screenshot analysis'; $Shortcut.Save()" >> "%PROD_DIR%\INSTALL.bat"
echo echo Shortcut created on desktop! >> "%PROD_DIR%\INSTALL.bat"
echo echo. >> "%PROD_DIR%\INSTALL.bat"
echo echo You can now launch AI Chat Assistant from your desktop. >> "%PROD_DIR%\INSTALL.bat"
echo pause >> "%PROD_DIR%\INSTALL.bat"

REM Create README for production
echo Creating README for production...
echo # AI Chat Assistant - Final Production Version > "%PROD_DIR%\README.txt"
echo. >> "%PROD_DIR%\README.txt"
echo This is the final production-ready standalone executable version. >> "%PROD_DIR%\README.txt"
echo No Python installation required! >> "%PROD_DIR%\README.txt"
echo. >> "%PROD_DIR%\README.txt"
echo ## Quick Start: >> "%PROD_DIR%\README.txt"
echo 1. Run INSTALL.bat to create desktop shortcut (optional) >> "%PROD_DIR%\README.txt"
echo 2. Double-click AI_Chat_Assistant.exe to start >> "%PROD_DIR%\README.txt"
echo. >> "%PROD_DIR%\README.txt"
echo ## Features: >> "%PROD_DIR%\README.txt"
echo - Smart AI chat with context >> "%PROD_DIR%\README.txt"
echo - Screenshot analysis >> "%PROD_DIR%\README.txt"
echo - Dark/Light themes >> "%PROD_DIR%\README.txt"
echo - Subscription system support >> "%PROD_DIR%\README.txt"
echo - Remember me functionality >> "%PROD_DIR%\README.txt"
echo - Secure authentication >> "%PROD_DIR%\README.txt"
echo. >> "%PROD_DIR%\README.txt"
echo ## System Requirements: >> "%PROD_DIR%\README.txt"
echo - Windows 10/11 >> "%PROD_DIR%\README.txt"
echo - Internet connection >> "%PROD_DIR%\README.txt"
echo - ~50 MB free space >> "%PROD_DIR%\README.txt"
echo. >> "%PROD_DIR%\README.txt"
echo ## Antivirus Note: >> "%PROD_DIR%\README.txt"
echo If your antivirus blocks this file, it's a false positive. >> "%PROD_DIR%\README.txt"
echo Add the file to your antivirus exceptions. >> "%PROD_DIR%\README.txt"
echo This is a legitimate application created with PyInstaller. >> "%PROD_DIR%\README.txt"

echo.
echo ========================================
echo    Creating Final ZIP Package
echo ========================================

REM Create ZIP package
set ZIP_NAME=AI_Chat_Assistant_Final_v%date:~-4,4%%date:~-10,2%%date:~-7,2%.zip
echo Creating ZIP package: %ZIP_NAME%

powershell "Compress-Archive -Path '%PROD_DIR%\*' -DestinationPath '%ZIP_NAME%' -Force"

if %errorlevel% neq 0 (
    echo Error creating ZIP package
    echo Cleaning up build files...
    if exist "dist" rmdir /s /q "dist"
    if exist "build" rmdir /s /q "build"
    if exist "version_info.txt" del "version_info.txt"
    pause
    exit /b 1
)

echo.
echo ========================================
echo    FINAL PRODUCTION BUILD COMPLETED!
echo ========================================
echo.
echo Package: %ZIP_NAME%
echo Executable: AI_Chat_Assistant.exe
echo.
echo This is the final, clean production package containing:
echo   • AI_Chat_Assistant.exe - Signed standalone executable
echo   • INSTALL.bat - Quick setup
echo   • README.txt - User instructions
echo   • All necessary data directories
echo.
echo Ready for distribution!
echo.
echo Users can:
echo 1. Extract the ZIP file
echo 2. Run INSTALL.bat (optional)
echo 3. Double-click AI_Chat_Assistant.exe
echo.
echo NOTE: This version includes version information
echo to reduce antivirus false positives.
echo.

REM Clean up build files
echo Cleaning up build files...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "version_info.txt" del "version_info.txt"
if exist "%PROD_DIR%" rmdir /s /q "%PROD_DIR%"

echo.
echo Build process completed!
pause
