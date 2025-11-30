@echo off
cls
echo ======================================================
echo          FULL ADVANCED ANDROID BUILD AUTOMATION 
echo                   AI GITA APP (Windows)
echo ======================================================
echo.

REM =====================================================
REM CONFIGURATION
REM =====================================================
set "PROJECT_ROOT=E:\gita_android_app"
set "APP_DIR=%PROJECT_ROOT%\android\app"
set "ASSETS_HTML=%APP_DIR%\src\main\assets\html\gita_shlokas.html"
set "AVD_NAME=Pixel_6"
set "APP_PACKAGE=com.gita.app"
set "GRADLEW=%PROJECT_ROOT%\android\gradlew.bat"

set "ANDROID_SDK=%LOCALAPPDATA%\Android\Sdk"
set "EMULATOR=%ANDROID_SDK%\emulator\emulator.exe"
set "ADB=%ANDROID_SDK%\platform-tools\adb.exe"

set "KEYSTORE=%PROJECT_ROOT%\release-key.jks"
set "KEY_ALIAS=myalias"
set "KEY_PASSWORD=123456"
set "STORE_PASSWORD=123456"


REM =====================================================
REM STEP 0: AUTO-INCREMENT VERSION CODE
REM =====================================================
echo STEP 0: Auto-Increment Version Code...
echo ------------------------------------------------------

set "GRADLE_FILE=%APP_DIR%\build.gradle"

for /f "tokens=2 delims== " %%a in ('findstr /C:"versionCode" "%GRADLE_FILE%"') do (
    set "CURRENT_CODE=%%a"
)

set /a NEW_VERSION_CODE=%CURRENT_CODE%+1

echo Updating versionCode from %CURRENT_CODE% to %NEW_VERSION_CODE%

powershell -Command "(Get-Content '%GRADLE_FILE%') -replace 'versionCode %CURRENT_CODE%', 'versionCode %NEW_VERSION_CODE%' | Set-Content '%GRADLE_FILE%'"

echo ✔ versionCode updated.
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 1: CLEAN PROJECT (DETAILED DELETED ITEMS + TREE)
REM =====================================================
echo STEP 1: Cleaning Project...
echo ------------------------------------------------------
echo.

setlocal enabledelayedexpansion
set "deleted_list="

echo 🔥 Deleting cache, temp, and pycache...

REM --- DELETE FILES ---
for /r "%PROJECT_ROOT%" %%f in (*.pyc *.log *.tmp *.bak *.temp) do (
    echo Deleted file: %%f
    del /q "%%f" >nul 2>&1
    set "deleted_list=!deleted_list!Deleted File: %%f\r\n"
)

REM --- DELETE __pycache__ DIRECTORIES ---
for /d /r "%PROJECT_ROOT%" %%d in (__pycache__) do (
    echo Deleted folder: %%d
    rmdir /s /q "%%d" >nul 2>&1
    set "deleted_list=!deleted_list!Deleted Folder: %%d\r\n"
)

echo ------------------------------------------------------
echo CLEAN-UP FINISHED
echo ------------------------------------------------------
echo.

echo 🗑 LIST OF DELETED ITEMS:
echo ------------------------------------------------------
echo(!deleted_list!
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 2: INSTALL PYTHON DEPENDENCIES
REM =====================================================
echo STEP 2: Installing Python dependencies...
pip install -r requirements.txt
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 3: GENERATE HTML
REM =====================================================
echo STEP 3: Generating Gita HTML Page...
python generate_html.py
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 4: VERIFY HTML EXISTENCE
REM =====================================================
echo STEP 4: Checking HTML...
if not exist "%ASSETS_HTML%" (
    echo ❌ ERROR: HTML not found at %ASSETS_HTML%
    pause
    exit /b
)
echo ✔ HTML found.
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 5: KILL OLD EMULATOR
REM =====================================================
echo STEP 5: Killing old emulator processes...
"%ADB%" kill-server >nul 2>&1
taskkill /IM qemu-system-x86_64.exe /F >nul 2>&1
taskkill /IM emulator.exe /F >nul 2>&1
echo ✔ Emulator processes terminated.
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 6: START EMULATOR
REM =====================================================
echo STEP 6: Starting Emulator...
start "" "%EMULATOR%" -avd %AVD_NAME%
timeout /t 20 >nul
echo ✔ Emulator running.
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 7: BUILD DEBUG APK
REM =====================================================
echo STEP 7: Building Debug APK...
cd /d "%PROJECT_ROOT%\android"
call "%GRADLEW%" assembleDebug
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 8: BUILD SIGNED RELEASE APK
REM =====================================================
echo STEP 8: Building Signed Release APK...
call "%GRADLEW%" assembleRelease ^
    -Pandroid.injected.signing.store.file="%KEYSTORE%" ^
    -Pandroid.injected.signing.store.password="%STORE_PASSWORD%" ^
    -Pandroid.injected.signing.key.alias="%KEY_ALIAS%" ^
    -Pandroid.injected.signing.key.password="%KEY_PASSWORD%"

echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 9: RELEASE APK CHECK
REM =====================================================
set "RELEASE_APK=%APP_DIR%\build\outputs\apk\release\app-release.apk"

if not exist "%RELEASE_APK%" (
    echo ❌ ERROR: Release APK missing!
    pause
    exit /b
)

echo ✔ Release APK Built Successfully!
echo APK: %RELEASE_APK%
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 10: INSTALL APK ON EMULATOR
REM =====================================================
echo STEP 10: Installing APK...
"%ADB%" install -r "%RELEASE_APK%"
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 11: LAUNCH APP
REM =====================================================
echo STEP 11: Launching application...
"%ADB%" shell monkey -p %APP_PACKAGE% -c android.intent.category.LAUNCHER 1
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 12: BACKUP ZIP
REM =====================================================
echo STEP 12: Creating project backup ZIP...
set "TS=%DATE%_%TIME%"
set "TS=%TS::=-%"
set "TS=%TS:/=-%"
set "TS=%TS: =_%"

set "ZIPFILE=GITA_BACKUP_%TS%.zip"

cd /d "%PROJECT_ROOT%"
powershell -Command "Compress-Archive -Path '*' -DestinationPath '%ZIPFILE%'"

echo ✔ Backup created: %ZIPFILE%
echo ------------------------------------------------------
echo.



REM =====================================================
REM STEP 13: FINAL DIRECTORY TREE (NEW)
REM =====================================================
echo STEP 13: FINAL DIRECTORY STRUCTURE:
echo ------------------------------------------------------
tree /f
echo ------------------------------------------------------
echo.



echo ======================================================
echo             FULL BUILD PROCESS COMPLETED!
echo         Press ANY KEY to close this window...
echo ======================================================
pause >nul
exit
