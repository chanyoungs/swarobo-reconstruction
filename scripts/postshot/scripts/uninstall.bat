@echo off
setlocal

:: 1. ADMINISTRATIVE PRIVILEGES CHECK
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
echo Administrative privileges confirmed.

:: 2. REMOVE REGISTRY ENTRIES
echo Removing context menu entries from the registry...

:: Remove the key for right-clicking ON a folder
reg delete "HKCR\Directory\shell\TrainWithPostshot" /f

:: Remove the key for right-clicking the BACKGROUND of a folder
reg delete "HKCR\Directory\Background\shell\TrainWithPostshot" /f

:: Check if deletion was successful
reg query "HKCR\Directory\shell\TrainWithPostshot" >nul 2>&1
if %errorLevel% equ 0 (
    echo [ERROR] Failed to remove the context menu entries. Please check your permissions.
) else (
    echo [OK] "Train with Postshot" has been successfully removed from the right-click menu.
)

echo.
pause
endlocal