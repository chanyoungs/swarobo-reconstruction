@echo off

:: Path to RealityScan executable
set RealityScanExe="%PROGRAMFILES%\Epic Games\RealityScan_2.0\RealityScan.exe"

:: Root folder of this script
set RootFolder=%~dp0

:: Input folder passed as argument
set ProjectFolder=%~1

:: Verify images folder exists
if not exist %ProjectFolder%\images (
    echo ERROR: %ProjectFolder%\images not found.
    echo.
    echo Press any key to continue...
    pause > nul
    exit /b 1
)

:: Path to images folder
set Images=%ProjectFolder%\images

:: Path to RealityScan settings
set SettingsFolder="%RootFolder%settings"

:: Path to save RealityScan project
set Project="%ProjectFolder%\RS.rsproj"

:: Run RealityScan
%RealityScanExe% -newScene ^
    -set "appIncSubdirs=true" ^
    -save %Project% ^
    -addFolder %Images% ^
    -align ^
    -selectMaximalComponent ^
    -exportRegistration %Images%\transforms.csv "%SettingsFolder%\export_reg_csv_settings.xml" ^
    -exportSparsePointCloud %Images%\sparse_pc.ply "%SettingsFolder%\export_ply_settings.xml" ^
    -save %Project% ^
    -quit
    
:: Check for errorlevel after RealityScan command
if %errorlevel% neq 0 (
    echo.
    echo ERROR: RealityScan command failed with exit code %errorlevel%.
    echo Press any key to continue...
    pause > nul
    exit /b %errorlevel%
)

echo.
echo Script completed successfully.
echo Press any key to continue...
pause > nul