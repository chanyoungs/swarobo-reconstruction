:: Aligns photos in RS and trains in PostShot

:: Path to RealityScan executable
set RealityScanExe="%PROGRAMFILES%\Epic Games\RealityScan_2.0\RealityScan.exe"

:: Root folder of this script
set RootFolder=%~dp0

:: Input folder passed as argument
set ProjectFolder=%~1

:: Verify images folder exists
if not exist "%ProjectFolder%\images" (
    echo ERROR: "%ProjectFolder%\images" not found.
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
