@echo off
setlocal enableextensions

:: --- Configuration ---
:: This sets the name of the Python script to be copied.
set "PYTHON_SCRIPT=Frame Extractor.py"

:: This defines the destination path. The trailing '\\.' is a robust way
:: to ensure the command prompt correctly interprets it as a folder.
set "RESOLVE_UTILITY_PATH=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility\Custom"

:: --- Script Logic ---
cls
echo ===================================================
echo  DaVinci Resolve Script Installer (v3 - Final)
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

echo [Step 2] Checking the destination folder...
if not exist "%RESOLVE_UTILITY_PATH%\" (
    echo          The destination folder does not exist. Creating it now...
    mkdir "%RESOLVE_UTILITY_PATH%"
)
echo          Destination is ready.
echo.

echo [Step 3] Copying the script...
copy /Y "%~dp0%PYTHON_SCRIPT%" "%RESOLVE_UTILITY_PATH%\"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ===================================================
    echo  SUCCESS! 🚀
    echo ===================================================
    echo.
    echo  The script was installed successfully.
    echo  Restart DaVinci Resolve to see it in the menu.
    echo.
) else (
    echo.
    echo ===================================================
    echo  ERROR!
    echo ===================================================
    echo.
    echo  The file could not be copied.
    echo  Please try running this batch file as an Administrator.
    echo.
)

:End
endlocal