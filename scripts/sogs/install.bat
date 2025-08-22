@echo off
setlocal

:: Get folder where this installer lives
set "INSTALL_DIR=%~dp0"
:: Remove trailing backslash
if "%INSTALL_DIR:~-1%"=="\" set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

:: Path to compress_with_sogs.bat and icon
set "SOGS_SCRIPT=%INSTALL_DIR%\compress_with_sogs.bat"
set "SOGS_ICON=%INSTALL_DIR%\sogs.ico"

:: Add context menu entry for .ply files
reg add "HKCR\SystemFileAssociations\.ply\shell\CompressWithSOGS" /ve /d "Compress with SOGS" /f
reg add "HKCR\SystemFileAssociations\.ply\shell\CompressWithSOGS" /v Icon /d "\"%SOGS_ICON%\"" /f
reg add "HKCR\SystemFileAssociations\.ply\shell\CompressWithSOGS" /v Position /d Top /f
reg add "HKCR\SystemFileAssociations\.ply\shell\CompressWithSOGS\command" /ve /d "\"%SOGS_SCRIPT%\" \"%%1\"" /f

endlocal