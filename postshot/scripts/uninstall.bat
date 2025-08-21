@echo off

:: Remove folder menu
reg delete "HKCR\Directory\shell\TrainWithPostshot" /f

:: Remove background menu
reg delete "HKCR\Directory\Background\shell\TrainWithPostshot" /f

echo.
echo [OK] "Train with Postshot" has been removed from the right-click menu.
echo.
