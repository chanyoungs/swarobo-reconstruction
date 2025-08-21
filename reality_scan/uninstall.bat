@echo off

:: Remove folder menu
reg delete "HKCR\Directory\shell\AlignWithRS" /f

:: Remove background menu
reg delete "HKCR\Directory\Background\shell\AlignWithRS" /f

echo.
echo [OK] "Align with RS" has been removed from the right-click menu.
echo.
