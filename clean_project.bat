@echo off
cls
echo ======================================================
echo         FULL ANDROID CI/CD PIPELINE (GITA APP)
echo ======================================================
echo.

:: -------------------------------------------------------
:: CONFIGURATION
:: -------------------------------------------------------
set "PROJECT_ROOT=E:\gita_android_app"
set "APP_DIR=%PROJECT_ROOT%\android\app"
set "ASSETS_HTML=%APP_DIR%\src\main\assets\html\gita_shlokas.html"
set "GRADLEW=%PROJECT_ROOT%\android\gradlew.bat"
set "APP_PACKAGE=com.gita.app"

set "AVD_NAME=Pixel_6"
set "ANDROID_SDK=%LOCALAPPDATA%\Android\Sdk"
set "EMULATOR=%ANDROID_SDK%\emulator\emulator.exe"
set "ADB=%ANDROID_SDK%\platform-tools\adb.exe"

:: Signing Info
set "KEYSTORE=E:\gita_android_app\release-key.jks"
set "KEY_ALIAS=myalias"
set "KEY_PASSWORD=123456"
set "STORE_PASSWORD=123456"

cd /d "%PROJECT_ROOT%"

:: ======================================================
:: STEP 0: AUTO-INCREMENT VERSION CODE
:: ======================================================
echo STEP 0: Auto-Incrementing versionCode...
echo ------------------------------------------------------
set "GRADLE_FILE=%APP_DIR%\build.gradle"

for /f "tokens=2 delims== " %%a in ('findstr /C:"versionCode" "%GRADLE_FILE%"') do (
    set "CURRENT_CODE=%%a"
)

set /a NEW_VERSION_CODE=%CURRENT_CODE%+1

echo Updating versionCode: %CURRENT_CODE% → %NEW_VERSION_CODE%
powershell -Command "(Get-Content '%GRADLE_FILE%') -replace 'versionCode %CURRENT_CODE%', 'versionCode %NEW_VERSION_CODE%' | Set-Content '%GRADLE_FILE%'"
echo ✔ versionCode updated.
echo.


:: ======================================================
:: STEP 1: CLEAN PROJECT
:: ======================================================
echo STEP 1: Cleaning old cache, logs, pycache...
echo ------------------------------------------------------

setlocal enabledelayedexpansion
set "deleted_list="

for /r %%f in (*.pyc *.log *.tmp *.bak *.temp) do (
    echo Deleted: %%f
    del /q "%%f" >nul 2>&1
    set "deleted_list=!deleted_list!Deleted: %%f\n"
)

for /d /r %%d in (__pycache__) do (
    echo Removed folder: %%d
    rmdir /s /q "%%d" >nul 2>&1
    set "deleted_list=!deleted_list!Removed: %%d\n"
)

echo.
echo Deleted Items:
echo ------------------------------------------------------
echo !deleted_list!
echo ------------------------------------------------------
echo.


:: ======================================================
:: STEP 2: INSTALL PYTHON DEPENDENCIES
:: ======================================================
echo STEP 2: Installing Python requirements...
pip install -r requirements.txt
echo.


:: ======================================================
:: STEP 3: GENERATE HTML FILE
:: ======================================================
echo STEP 3: Generating gita_shlokas.html
python generate_html.py
echo.

if not exist "%ASSETS_HTML%" (
    echo ❌ ERROR: Missing HTML file!
    pause
    exit /b
)
echo ✔ HTML generated at: %ASSETS_HTML%
echo.


:: ======================================================
:: STEP 4: KILL OLD EMULATORS
:: ======================================================
echo STEP 4: Killing any running emulator...
"%ADB%" kill-server >nul 2>&1
taskkill /IM qemu-system-x86_64.exe /F >nul 2>&1
taskkill /IM emulator.exe /F >nul 2>&1
echo ✔ Emulator cleaned.
echo.


:: ======================================================
:: STEP 5: START EMULATOR
:: ======================================================
echo STEP 5: Starting Android Emulator (%AVD_NAME%)...
start "" "%EMULATOR%" -avd %AVD_NAME%
timeout /t 20 >nul
echo ✔ Emulator Started.
echo.


:: ======================================================
:: STEP 6: GRADLE DEBUG BUILD
:: ======================================================
echo STEP 6: Building Debug APK...
cd /d "%PROJECT_ROOT%\android"
call "%GRADLEW%" assembleDebug
echo ✔ Debug APK built.
echo.


:: ======================================================
:: STEP 7: SIGNED RELEASE BUILD
:: ======================================================
echo STEP 7: Building Signed Release APK...
call "%GRADLEW%" assembleRelease ^
  -Pandroid.injected.signing.store.file="%KEYSTORE%" ^
  -Pandroid.injected.signing.store.password="%STORE_PASSWORD%" ^
  -Pandroid.injected.signing.key.alias="%KEY_ALIAS%" ^
  -Pandroid.injected.signing.key.password="%KEY_PASSWORD%"
echo.

set "RELEASE_APK=%APP_DIR%\build\outputs\apk\release\app-release.apk"

if not exist "%RELEASE_APK%" (
    echo ❌ ERROR: Release APK missing!
    pause
    exit /b
)

echo ✔ Release APK generated: %RELEASE_APK%
echo.


:: ======================================================
:: STEP 8: INSTALL APK ON EMULATOR
:: ======================================================
echo STEP 8: Installing APK on emulator...
"%ADB%" install -r "%RELEASE_APK%"
echo ✔ APK Installed.
echo.


:: ======================================================
:: STEP 9: LAUNCH APP
:: ======================================================
echo STEP 9: Launching Gita Android App...
"%ADB%" shell monkey -p %APP_PACKAGE% -c android.intent.category.LAUNCHER 1
echo ✔ App Launched.
echo.


:: ======================================================
:: STEP 10: ZIP BACKUP
:: ======================================================
echo STEP 10: Creating ZIP Backup of project...
set "TS=%DATE%_%TIME%"
set "TS=%TS::=-%"
set "TS=%TS:/=-%"
set "TS=%TS: =_%"

set "ZIPFILE=GITA_BACKUP_%TS%.zip"

cd /d "%PROJECT_ROOT%"
powershell -Command "Compress-Archive -Path '*' -DestinationPath '%ZIPFILE%'"

echo ✔ Backup Created: %ZIPFILE%
echo.


:: ======================================================
:: STEP 11: PRINT FINAL DIRECTORY STRUCTURE
:: ======================================================
echo **********************************************
echo FINAL DIRECTORY STRUCTURE
echo **********************************************
echo.

tree /f

echo.
echo ======================================================
echo CI/CD Pipeline Completed Successfully!
echo Press ANY KEY to exit...
echo ======================================================
pause >nul
exit
