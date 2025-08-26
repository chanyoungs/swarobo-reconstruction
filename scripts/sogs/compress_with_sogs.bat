@echo off
setlocal

if "%~1"=="" (
    exit /b 1
)

:loop
if "%~1"=="" goto end

:: Current .ply file
set "ply_path=%~1"

:: Remove extension and append _sogs for output directory
set "output_dir=%~dpn1_sogs"

:: Run sogs-compress
"C:\Users\chans\anaconda3\envs\torch128\Scripts\sogs-compress.exe" --ply "%ply_path%" --output-dir "%output_dir%"

:: Shift to next argument
shift
goto loop

:end
endlocal
pause