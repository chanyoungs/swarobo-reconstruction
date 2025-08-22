@echo off
setlocal enabledelayedexpansion

:: Check args
if "%~1"=="" (
    echo Usage: %~nx0 INPUT_FOLDER
    exit /b 1
)

:: Input argument
set INPUT_FOLDER=%~1

:: Verify images folder exists
if not exist "%INPUT_FOLDER%\images" (
    echo ERROR: "%INPUT_FOLDER%\images" not found.
    exit /b 1
)

:: Get folder name
for %%I in ("%INPUT_FOLDER%") do (
    set SCENE_NAME=%%~nI
)

:: Paths
set PROJECT_FILE=%INPUT_FOLDER%\%SCENE_NAME%.psht
set OUTPUT_DIR=%INPUT_FOLDER%\output
set OUTPUT_PLY=%OUTPUT_DIR%\%SCENE_NAME%.ply

:: Ensure output folder exists
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

:: Run Postshot CLI
echo Running training on "%INPUT_FOLDER%\images" ...
"%PROGRAMFILES%\Jawset Postshot\bin\postshot-cli.exe" train ^
    -i "%INPUT_FOLDER%\images" ^
    -p "Splat ADC" ^
    --image-select all ^
    --max-image-size 0 ^
    --store-training-context ^
    -o "%PROJECT_FILE%" ^
    --export-splat-ply "%OUTPUT_PLY%"

echo.
echo Training finished.
echo Project: %PROJECT_FILE%
echo Splat PLY: %OUTPUT_PLY%
endlocal
