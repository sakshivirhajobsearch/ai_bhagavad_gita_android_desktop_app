@echo off
title Cleaning Gita Android Project...
echo ===============================
echo  CLEANING PROJECT FOLDERS
echo ===============================

set ROOT_DIR=%cd%

echo.
echo Removing __pycache__ folders except data folder's core files...

REM Delete python __pycache__ safely (inside data only flush .pyc)
if exist "%ROOT_DIR%\data\__pycache__" (
    del /f /q "%ROOT_DIR%\data\__pycache__\*.pyc"
    rmdir /s /q "%ROOT_DIR%\data\__pycache__"
    echo ✅ data/__pycache__ cleaned.
)

REM Remove utils directory
if exist "%ROOT_DIR%\utils" (
    rmdir /s /q "%ROOT_DIR%\utils"
    echo ✅ utils folder removed.
)

REM Remove Android build directories
if exist "%ROOT_DIR%\android\app\build" (
    rmdir /s /q "%ROOT_DIR%\android\app\build"
    echo ✅ android/app/build removed.
)

if exist "%ROOT_DIR%\android\.gradle" (
    rmdir /s /q "%ROOT_DIR%\android\.gradle"
    echo ✅ android/.gradle removed.
)

REM Remove junk files
del /f /q "%ROOT_DIR%\*.log" 2>nul
del /f /q "%ROOT_DIR%\*.tmp" 2>nul
del /f /q "%ROOT_DIR%\*.bak" 2>nul

echo.
echo ===============================
echo ✅ CLEAN PROJECT COMPLETED
echo ===============================
pause
