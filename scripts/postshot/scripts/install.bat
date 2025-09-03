@echo off
setlocal

:: 1. ADMINISTRATIVE PRIVILEGES CHECK
:: This section checks for admin rights and re-launches the script as admin if needed.
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
echo Administrative privileges confirmed.

:: 2. DEFINE PATHS
:: Get the directory where this installer script is located.
set "INSTALL_DIR=%~dp0"
:: Remove trailing backslash if it exists.
if "%INSTALL_DIR:~-1%"=="\" set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

:: Path to the script that will be executed by the context menu.
set "TRAIN_SCRIPT=%INSTALL_DIR%\train_postshot.bat"

:: Check if the training script actually exists.
if not exist "%TRAIN_SCRIPT%" (
    echo [ERROR] The script 'train_postshot.bat' was not found in this folder.
    echo Please ensure the installer and the training script are in the same directory.
    pause
    exit /b
)

:: 3. LOCATE POSTSHOT EXECUTABLE FOR THE ICON
set "POSTSHOT_ICON="
set "POSTSHOT_PATH_64=%ProgramFiles%\Jawset Postshot\bin\postshot.exe"
set "POSTSHOT_PATH_32=%ProgramFiles(x86)%\Jawset Postshot\bin\postshot.exe"

if exist "%POSTSHOT_PATH_64%" (
    set "POSTSHOT_ICON=%POSTSHOT_PATH_64%"
) else if exist "%POSTSHOT_PATH_32%" (
    set "POSTSHOT_ICON=%POSTSHOT_PATH_32%"
)

if defined POSTSHOT_ICON (
    echo Found Postshot icon at: "%POSTSHOT_ICON%"
) else (
    echo [WARNING] Could not find postshot.exe. The menu item will be created without an icon.
)

:: 4. ADD REGISTRY ENTRIES
echo Adding context menu entries to the registry...

:: Key for right-clicking ON a folder
set "FOLDER_MENU_KEY=HKCR\Directory\shell\TrainWithPostshot"
reg add "%FOLDER_MENU_KEY%" /ve /d "Train with Postshot" /f
if defined POSTSHOT_ICON ( reg add "%FOLDER_MENU_KEY%" /v Icon /d "\"%POSTSHOT_ICON%\"" /f )
reg add "%FOLDER_MENU_KEY%" /v Position /d "Top" /f
reg add "%FOLDER_MENU_KEY%\command" /ve /d "\"%TRAIN_SCRIPT%\" \"%%1\"" /f

:: Key for right-clicking the BACKGROUND of a folder
set "BACKGROUND_MENU_KEY=HKCR\Directory\Background\shell\TrainWithPostshot"
reg add "%BACKGROUND_MENU_KEY%" /ve /d "Train with Postshot" /f
if defined POSTSHOT_ICON ( reg add "%BACKGROUND_MENU_KEY%" /v Icon /d "\"%POSTSHOT_ICON%\"" /f )
reg add "%BACKGROUND_MENU_KEY%" /v Position /d "Top" /f
reg add "%BACKGROUND_MENU_KEY%\command" /ve /d "\"%TRAIN_SCRIPT%\" \"%%V\"" /f

:: 5. FINAL CONFIRMATION
echo.
echo [OK] "Train with Postshot" has been successfully added to the folder right-click menu.
echo When you select multiple folders, the script will run once for each folder, one after the other.
echo.
pause
endlocal