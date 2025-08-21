@echo off
setlocal

:: Get folder where this installer lives
set INSTALL_DIR=%~dp0
:: Remove trailing backslash
if "%INSTALL_DIR:~-1%"=="\" set INSTALL_DIR=%INSTALL_DIR:~0,-1%

:: Path to train_postshot.bat (same folder as installer)
set TRAIN_SCRIPT=%INSTALL_DIR%\train_postshot.bat

:: Path to Postshot executable for icon
set POSTSHOT_ICON=%PROGRAMFILES%\Jawset Postshot\bin\postshot.exe

:: === Add context menu entries ===
:: Folder menu
reg add "HKCR\Directory\shell\TrainWithPostshot" /ve /d "Train with Postshot" /f
reg add "HKCR\Directory\shell\TrainWithPostshot" /v Icon /d "\"%POSTSHOT_ICON%\"" /f
reg add "HKCR\Directory\shell\TrainWithPostshot" /v Position /d Top /f
reg add "HKCR\Directory\shell\TrainWithPostshot\command" /ve /d "\"%TRAIN_SCRIPT%\" \"%%1\"" /f

:: Background menu
reg add "HKCR\Directory\Background\shell\TrainWithPostshot" /ve /d "Train with Postshot" /f
reg add "HKCR\Directory\Background\shell\TrainWithPostshot" /v Icon /d "\"%POSTSHOT_ICON%\"" /f
reg add "HKCR\Directory\Background\shell\TrainWithPostshot" /v Position /d Top /f
reg add "HKCR\Directory\Background\shell\TrainWithPostshot\command" /ve /d "\"%TRAIN_SCRIPT%\" \"%%V\"" /f

echo.
echo [OK] "Train with Postshot" has been added to the right-click menu.
echo Folder path will automatically be passed to train_postshot.bat.
echo.
endlocal
