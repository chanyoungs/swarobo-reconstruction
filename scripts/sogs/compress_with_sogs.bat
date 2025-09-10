@echo off
setlocal

if "%~1"=="" (
    echo No input files provided.
    echo Usage: %0 file1.ply file2.ply ...
    exit /b 1
)

:loop
if "%~1"=="" goto end

:: Current .ply file
set "ply_path=%~1"

:: Remove extension and append _sogs for output directory
set "output_dir=%~dpn1_sogs_v2"

:: Create the output directory if it does not exist
if not exist "%output_dir%" (
    echo Creating directory: %output_dir%
    mkdir "%output_dir%"
)

:: Run sogs-compress
echo Processing %ply_path%...
splat-transform "%ply_path%" "%output_dir%\meta.json"

:: Shift to next argument
shift
goto loop

:end
echo.
echo All files processed.
endlocal
pause
