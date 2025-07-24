::Aligns photos in RS and trains in PostShot

:: path to RealityScan and PostShot directories
set RealityScanExe="C:\Program Files\Epic Games\RealityScan_2.0\RealityScan.exe"

:: root path of project (%~dp0 means the folder in which this script is stored)
set RootFolder=%~dp0

set ProjectFolder=%~1

:: set path to the folder with your images
set Images=%ProjectFolder%

:: set the path to RealityScan settings
set SettingsFolder="%RootFolder%settings"

:: set the path, where project is going to be saved, and its name
set Project="%ProjectFolder%\RS.rsproj"

:: run RealityScan
%RealityScanExe% -newScene ^
	-set "appIncSubdirs=true" ^
    -save %Project% ^
    -addFolder %ProjectFolder% ^
    -align ^
    -selectMaximalComponent ^
    -exportRegistration %ProjectFolder%\transforms.csv "%SettingsFolder%\export_reg_csv_settings.xml" ^
    -exportSparsePointCloud %ProjectFolder%\sparse_pc.ply "%SettingsFolder%\export_ply_settings.xml" ^
    -save %Project% ^
	-quit