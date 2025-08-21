@echo off
setlocal

:: Get folder where this installer lives
set INSTALL_DIR=%~dp0
:: Remove trailing backslash
if "%INSTALL_DIR:~-1%"=="\" set INSTALL_DIR=%INSTALL_DIR:~0,-1%

:: Path to RS_SFM_PS.BAT (same folder as installer)
set TRAIN_SCRIPT=%INSTALL_DIR%\RS_SFM_PS.BAT

:: Path to Reality Scan executable for icon
set RS_ICON=%PROGRAMFILES%\Epic Games\RealityScan_2.0\RealityScan.exe

:: === Add context menu entries ===
:: Folder menu
reg add "HKCR\Directory\shell\AlignWithRS" /ve /d "Align with RS" /f
reg add "HKCR\Directory\shell\AlignWithRS" /v Icon /d "\"%RS_ICON%\"" /f
reg add "HKCR\Directory\shell\AlignWithRS" /v Position /d Top /f
reg add "HKCR\Directory\shell\AlignWithRS\command" /ve /d "\"%TRAIN_SCRIPT%\" \"%%1\"" /f

:: Background menu
reg add "HKCR\Directory\Background\shell\AlignWithRS" /ve /d "Align with RS" /f
reg add "HKCR\Directory\Background\shell\AlignWithRS" /v Icon /d "\"%RS_ICON%\"" /f
reg add "HKCR\Directory\Background\shell\AlignWithRS" /v Position /d Top /f
reg add "HKCR\Directory\Background\shell\AlignWithRS\command" /ve /d "\"%TRAIN_SCRIPT%\" \"%%V\"" /f

echo.
echo [OK] "Align with RS" has been added to the right-click menu.
echo Folder path will automatically be passed to RS_SFM_PS.BAT.
echo.
endlocal
