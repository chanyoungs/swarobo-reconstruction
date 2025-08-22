@echo off
setlocal

:: === Remove context menu entry for .ply files ===
reg delete "HKCR\SystemFileAssociations\.ply\shell\CompressWithSOGS" /f

echo.
echo [OK] "Compress with SOGS" has been removed from the right-click menu for .ply files.
echo.
endlocal
