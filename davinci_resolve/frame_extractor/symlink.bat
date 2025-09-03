@echo off
setlocal enableextensions

:: =================================================================================
:: DaVinci Resolve Script Symlinker
::
:: This script creates a symbolic link from 'frame_extractor.py' in this folder
:: to the DaVinci Resolve Utility Scripts folder.
:: This allows you to edit the script here, and the changes will be live in Resolve.
::
:: IMPORTANT: This script MUST be run as an Administrator.
:: =================================================================================

:: --- Configuration ---
set "PYTHON_SCRIPT=Frame Extractor.py"
set "RESOLVE_UTILITY_PATH=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility\Custom"

:: --- Administrator Check ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [Requesting Administrator privileges...]
    powershell -Command "Start-Process -FilePath '%~s0' -Verb RunAs"
    exit /b
)

:: --- Script Logic ---
cls
echo ===================================================
echo  DaVinci Resolve Script Symlinker
echo ===================================================
echo.

echo [Step 1] Verifying that '%PYTHON_SCRIPT%' is present...
if not exist "%~dp0%PYTHON_SCRIPT%" (
    echo.
    echo [ERROR] Could not find '%PYTHON_SCRIPT%'.
    echo         Please make sure this batch file and the Python script
    echo         are in the same folder.
    goto End
)
echo          Found it!
echo.

echo [Step 2] Preparing the destination folder...
if not exist "%RESOLVE_UTILITY_PATH%\" (
    echo          Destination folder not found. Creating it...
    mkdir "%RESOLVE_UTILITY_PATH%"
)
echo          Destination is ready.
echo.

set "LINK_PATH=%RESOLVE_UTILITY_PATH%\%PYTHON_SCRIPT%"
set "TARGET_PATH=%~dp0%PYTHON_SCRIPT%"

echo [Step 3] Checking for existing files or links...
if exist "%LINK_PATH%" (
    echo          An existing file or link was found. Removing it first...
    del "%LINK_PATH%"
)
echo          Ready to create the link.
echo.

echo [Step 4] Creating the symbolic link...
echo          Link: %LINK_PATH%
echo          Target: %TARGET_PATH%
echo.

mklink "%LINK_PATH%" "%TARGET_PATH%"

if %errorlevel% equ 0 (
    echo ===================================================
    echo  SUCCESS! 🚀
    echo ===================================================
    echo.
    echo  A symbolic link was created successfully.
    echo  Restart DaVinci Resolve to see the script in the menu.
    echo.
) else (
    echo ===================================================
    echo  ERROR!
    echo ===================================================
    echo.
    echo  Failed to create the symbolic link.
    echo  Please ensure you are running this batch file as an Administrator.
    echo.
)

:End
echo Press any key to exit.
pause > nul
endlocal