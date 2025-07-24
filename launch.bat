@echo off
title Perplexity AI GUI Client - Enhanced Edition v2.0

echo.
echo ========================================================
echo  Perplexity AI GUI Client - Enhanced Edition v2.0
echo ========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo    Please install Python 3.7+ and try again
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: pip is not available
    echo    Please ensure pip is installed with Python
    pause
    exit /b 1
)

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo 📦 Installing/checking dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Launch the application
echo.
echo 🚀 Starting Perplexity AI GUI Client...
echo    Close this window to stop the application
echo ========================================================
echo.

python launch.py

if errorlevel 1 (
    echo.
    echo ❌ Application exited with an error
    pause
)

echo.
echo 👋 Application closed
pause