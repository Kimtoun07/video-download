@echo off
REM ═══════════════════════════════════════════════════════════
REM  GrabVid Installer for Windows
REM ═══════════════════════════════════════════════════════════

echo.
echo    ╔══════════════════════════════════════╗
echo    ║  GrabVid Installer                  ║
echo    ║  Universal Video Downloader          ║
echo    ╚══════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed.
    echo   Download from: https://python.org
    echo   Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo   [OK] Python detected

REM Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed.
    pause
    exit /b 1
)
echo   [OK] pip detected

echo.
echo   Installing GrabVid...
echo.

REM Install core dependencies
echo   Installing core dependencies...
pip install --upgrade yt-dlp click

REM Check for --gui flag
if "%1"=="--gui" (
    echo   Installing GUI dependencies...
    pip install --upgrade customtkinter Pillow
)

if "%1"=="--all" (
    echo   Installing GUI and optional dependencies...
    pip install --upgrade customtkinter Pillow pyperclip mutagen requests
)

REM Install the package
echo   Installing GrabVid package...
pip install -e .

echo.
echo ═══════════════════════════════════════════
echo   GrabVid installed successfully!
echo ═══════════════════════════════════════════
echo.
echo   Usage:
echo     grabvid [url]              Download a video
echo     grabvid batch [file]       Batch download
echo     grabvid episodes [url]     Download playlist
echo     grabvid info [url]         Show video info
echo     grabvid gui                Launch GUI
echo     grabvid platforms          List platforms
echo.
echo   Quick start:
echo     grabvid https://youtube.com/watch?v=example
echo.

pause
