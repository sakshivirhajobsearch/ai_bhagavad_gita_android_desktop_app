@echo off
echo ============================================
echo    CLEANING ANDROID GITA APP PROJECT
echo ============================================
echo.

REM ------------------------------
REM REMOVE PYTHON CACHE FILES
REM ------------------------------
echo 🔹 Removing Python cache files...
for /r %%i in (__pycache__) do (
    echo Deleting: %%i
    rmdir /s /q "%%i" 2>nul
)

del /s /q *.pyc 2>nul

echo Done.
echo.

REM ------------------------------
REM CLEAN ANDROID BUILD FOLDERS
REM ------------------------------
echo 🔹 Cleaning Android build directories...

IF EXIST android\app\build (
    echo Removing android\app\build ...
    rmdir /s /q android\app\build
)

IF EXIST android\build (
    echo Removing android\build ...
    rmdir /s /q android\build
)

echo Done.
echo.

REM ------------------------------
REM REMOVE OLD HTML FILES
REM ------------------------------
echo 🔹 Removing OLD html output files...

IF EXIST android\app\src\main\assets\html\gita_problems.html (
    del /q android\app\src\main\assets\html\gita_problems.html
    echo Deleted gita_problems.html
)

IF EXIST android\app\src\main\assets\html\index.html (
    del /q android\app\src\main\assets\html\index.html
    echo Deleted index.html
)

REM KEEP ONLY gita_shlokas.html
echo Keeping gita_shlokas.html
echo.

REM ------------------------------
REM DO NOT DELETE data FOLDER
REM ------------------------------
echo 🔒 Skipping deletion of the "data" folder (important)
echo.

REM ------------------------------
REM CLEAN LOGS & TEMP FILES
REM ------------------------------
echo 🔹 Cleaning temporary files...
del /s /q *.log *.tmp 2>nul

echo Done.
echo.

echo ============================================
echo Project Cleaned Successfully!
echo ============================================
pause
