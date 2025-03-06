@echo off
:: Change to the directory where the batch file is located
cd /d "%~dp0"

:: Check if pythonw.exe is available in PATH
where pythonw.exe >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: pythonw.exe not found in PATH
    echo Please ensure Python is installed correctly.
    pause
    exit /b 1
)

:: Run the macrorecorder script without console window
start "" pythonw.exe launch_macrorecorder.pyw

:: Exit the batch file
exit /b 0 