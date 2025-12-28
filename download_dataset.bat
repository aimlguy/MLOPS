@echo off
REM Quick Dataset Download Script for Windows
REM This script attempts to download the Kaggle dataset automatically

echo.
echo ================================================================
echo   KAGGLE DATASET DOWNLOADER - No-Show Appointments
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python first.
    pause
    exit /b 1
)

echo Running automated downloader...
echo.

python scripts\download_dataset.py

echo.
echo ================================================================
echo   DOWNLOAD COMPLETE
echo ================================================================
echo.
echo Next steps:
echo   1. Verify: python scripts\setup_check.py
echo   2. Train:  python scripts\run_workflow.py
echo.
pause
