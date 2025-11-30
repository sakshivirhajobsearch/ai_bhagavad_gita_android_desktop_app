@echo off
cls

echo **********************************************
echo Files from main directory : E:\gita_android_app
echo **********************************************
echo.

set "PROJECT_ROOT=E:\gita_android_app"
cd /d "%PROJECT_ROOT%"

:: ======================================================
:: 1. DELETE ITEMS IN SEQUENCE
:: ======================================================

echo -------- Cleaning python cache, temp & useless files --------
echo.

setlocal enabledelayedexpansion
set "deleted_list="

:: ---- Delete files: pyc, log, tmp, bak, temp ----
for /r %%f in (*.pyc *.log *.tmp *.bak *.temp) do (
    echo Deleted: %%f
    del /q "%%f" >nul 2>&1
    set "deleted_list=!deleted_list!Deleted: %%f\n"
)

:: ---- Delete __pycache__ folders ----
for /d /r %%d in (__pycache__) do (
    echo Removed folder: %%d
    rmdir /s /q "%%d" >nul 2>&1
    set "deleted_list=!deleted_list!Removed folder: %%d\n"
)

echo.
echo -------- CLEANUP COMPLETED --------
echo.

:: ======================================================
:: 2. PRINT ALL DELETED ITEMS
:: ======================================================

echo ------------------ Deleted Items ----------------------
echo If nothing appears below, no redundant files existed.
echo.

echo !deleted_list!
echo -------------------------------------------------------
echo.


:: ======================================================
:: 3. PRINT FINAL DIRECTORY STRUCTURE
:: EXACT TREE FORMAT LIKE YOUR SAMPLE
:: ======================================================

echo **********************************************
echo FINAL DIRECTORY STRUCTURE
echo **********************************************
echo.

tree /f

echo.
echo **********************************************
echo Operation Completed Successfully.
echo Press ANY KEY to exit...
echo **********************************************
pause >nul
exit
