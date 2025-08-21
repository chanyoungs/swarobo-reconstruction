::Aligns photos in RS and trains in PostShot

:: path to RealityScan and PostShot directories
set RealityScanExe="%PROGRAMFILES%\Epic Games\RealityScan_2.0\RealityScan.exe"

:: root path of project (%~dp0 means the folder in which this script is stored)
set RootFolder=%~dp0

set ProjectFolder=%~1

:: set path to the folder with your images
set Images="%ProjectFolder%\images"

:: set the path to RealityScan settings
set SettingsFolder="%RootFolder%settings"

:: set the path, where project is going to be saved, and its name
set Project="%ProjectFolder%\RS.rsproj"

:: set project name as data_folderName
for %%F in (%ProjectFolder%) do set ProjectName=data_%%~nxF

:: make export dirs
mkdir %ProjectFolder%\%ProjectName%\images

:: run RealityScan
%RealityScanExe% -newScene ^
	-set "appIncSubdirs=true" ^
        -addFolder %Images% ^
        -save %Project% ^
        -align ^
        -selectMaximalComponent ^
        -exportRegistration %ProjectFolder%\%ProjectName%\images\transforms.json "%SettingsFolder%\export_reg_settings.xml" ^
        -exportSparsePointCloud %ProjectFolder%\%ProjectName%\sparse_pc.ply "%SettingsFolder%\export_ply_settings.xml" ^
        -save %Project% ^
	-quit 