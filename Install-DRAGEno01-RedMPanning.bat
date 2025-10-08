@echo off
setlocal enabledelayedexpansion

:: Set console colors and title
title DRAGEno01 RedM Auto Panning - Installer
color 0A

:: Display header
echo.
echo ================================================================
echo           DRAGEno01 RedM Auto Panning - Installer
echo ================================================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running with administrator privileges
) else (
    echo [WARNING] Not running as administrator - some features may be limited
)
echo.

:: Check Python version support
echo [INFO] Checking Python version support...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/info.txt' -TimeoutSec 10; $content = $response.Content; Write-Output $content } catch { Write-Output 'ERROR: Failed to fetch Python version info' }" > temp_python_info.txt

set "python_supported="
set "python_version="
if exist temp_python_info.txt (
    for /f "usebackq delims=" %%a in ("temp_python_info.txt") do (
        echo %%a | findstr /r "supported.*=" >nul && (
            for /f "tokens=2 delims==" %%b in ("%%a") do (
                set "temp_value=%%b"
                call :trim_spaces python_supported "%%temp_value%%"
            )
        )
        echo %%a | findstr /r "version.*=" >nul && (
            for /f "tokens=2 delims==" %%b in ("%%a") do (
                set "temp_value=%%b"
                call :trim_spaces python_version "%%temp_value%%"
            )
        )
    )
    del temp_python_info.txt
)

:: Check if Python version is supported
if "%python_supported%"=="false" (
    echo [ERROR] Python version is not supported
    echo [INFO] Please visit: https://github.com/DRAGEno01/RedM-Auto-Panning/releases
    echo [INFO] to download a supported version
    pause
    exit /b 1
)

:: Set Python as the only option
set "version=Python"
set "info_url=https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/info.txt"
set "main_file=RedMPanning.py"
set "requirements_file=requirements.txt"
set "run_file=RedM Auto Panner.bat"
set "version_number=%python_version%"

echo.
echo [INFO] Selected %version% version
echo.

:: Inform user about runtime requirements
if "%version%"=="Python" (
    echo [INFO] Python Version Selected
    echo [NOTE] Make sure you have Python installed before running the program
    echo [NOTE] Download Python from: https://www.python.org/downloads/
    echo [NOTE] Make sure to check "Add Python to PATH" during installation
) else if "%version%"=="Java" (
    echo [INFO] Java Version Selected
    echo [NOTE] Make sure you have Java installed before running the program
    echo [NOTE] Download Java from: https://www.oracle.com/java/technologies/downloads/
    echo [NOTE] Or use OpenJDK: https://adoptium.net/
)

echo.
echo [INFO] Version %version_number% is supported
echo [DEBUG] Version number: '%version_number%'

echo.
echo [INFO] Creating installation directory...

:: Create main directory on Desktop
set "desktop=%USERPROFILE%\Desktop"
set "main_dir=%desktop%\DRAGEno01 RedM Panner"
set "version_dir=%main_dir%\%version%"
set "src_dir=%version_dir%\src"

:: Create directories
if not exist "%main_dir%" mkdir "%main_dir%"
if not exist "%version_dir%" mkdir "%version_dir%"
if not exist "%src_dir%" mkdir "%src_dir%"

echo [SUCCESS] Created directory: %main_dir%
echo [SUCCESS] Created directory: %version_dir%
echo [SUCCESS] Created directory: %src_dir%

echo.
echo [INFO] Downloading files...

:: Download main file
echo [INFO] Downloading %main_file%...
if "%version_number%"=="" (
    echo [WARNING] Version number is empty, trying fallback URL...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/lib/src/%main_file%' -OutFile '%src_dir%\%main_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %main_file%' } catch { Write-Output 'ERROR: Failed to download %main_file%' }"
) else (
    powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/V%version_number%/%main_file%' -OutFile '%src_dir%\%main_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %main_file%' } catch { Write-Output 'ERROR: Failed to download %main_file%' }"
)

if not exist "%src_dir%\%main_file%" (
    echo [ERROR] Failed to download %main_file%
    pause
    exit /b 1
)

:: Download requirements file
echo [INFO] Downloading %requirements_file%...
powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/%requirements_file%' -OutFile '%src_dir%\%requirements_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %requirements_file%' } catch { Write-Output 'WARNING: Failed to download %requirements_file%' }"

:: Note: Setup.bat files are not available in the repository

:: Create run script
echo [INFO] Creating run script...
echo @echo off > "%version_dir%\%run_file%"
echo cd /d "%%~dp0" >> "%version_dir%\%run_file%"
echo if not exist "src\%main_file%" ^( >> "%version_dir%\%run_file%"
echo     echo [ERROR] Main file not found. Please run the installer first. >> "%version_dir%\%run_file%"
echo     echo [INFO] To download the installer, visit: https://github.com/DRAGEno01/RedM-Auto-Panning/releases >> "%version_dir%\%run_file%"
echo     pause >> "%version_dir%\%run_file%"
echo     exit /b 1 >> "%version_dir%\%run_file%"
echo ^) >> "%version_dir%\%run_file%"
echo cd src >> "%version_dir%\%run_file%"
echo :: Check for Python executables in order of preference >> "%version_dir%\%run_file%"
echo :: 1. Try pythonw (no console) >> "%version_dir%\%run_file%"
echo pythonw --version ^>nul 2^>^&1 >> "%version_dir%\%run_file%"
echo if %%errorLevel%% == 0 ^( >> "%version_dir%\%run_file%"
echo     :: pythonw available - run without console >> "%version_dir%\%run_file%"
echo     start /min pythonw %main_file% >> "%version_dir%\%run_file%"
echo ^) else ^( >> "%version_dir%\%run_file%"
echo     :: 2. Try python3 (if available) >> "%version_dir%\%run_file%"
echo     python3 --version ^>nul 2^>^&1 >> "%version_dir%\%run_file%"
echo     if %%errorLevel%% == 0 ^( >> "%version_dir%\%run_file%"
echo         :: python3 available - run with console >> "%version_dir%\%run_file%"
echo         start /min python3 %main_file% >> "%version_dir%\%run_file%"
echo     ^) else ^( >> "%version_dir%\%run_file%"
echo         :: 3. Fallback to python >> "%version_dir%\%run_file%"
echo         :: python available - run with console >> "%version_dir%\%run_file%"
echo         start /min python %main_file% >> "%version_dir%\%run_file%"
echo     ^) >> "%version_dir%\%run_file%"
echo ^) >> "%version_dir%\%run_file%"
echo exit >> "%version_dir%\%run_file%"

echo [SUCCESS] Created run script: %version_dir%\%run_file%

:: Install Python dependencies in src folder
echo.
echo [INFO] Installing Python dependencies in src folder...
echo [INFO] This may take a few moments...

:: Check if Python is available
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Python is available, installing dependencies...
    
    :: Check if pythonw is available
    pythonw --version >nul 2>&1
    if %errorLevel% == 0 (
        echo [INFO] pythonw.exe is available - console will be hidden
    ) else (
        echo [WARNING] pythonw.exe not found - console may be visible
        echo [INFO] This is normal if Python was installed without GUI support
    )
    
    :: Detect Python version for run script
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "detected_python_version=%%i"
    echo [INFO] Detected Python version: %detected_python_version%
    
    :: Change to src directory
    cd /d "%src_dir%"
    
    :: Install pynput in src folder
    echo [INFO] Installing pynput in src folder...
    python -m pip install pynput>=1.7.6
    
    :: Install psutil in src folder  
    echo [INFO] Installing psutil in src folder...
    python -m pip install psutil>=5.9.0
    
    echo [SUCCESS] Python dependencies installed in src folder
) else (
    echo [WARNING] Python not found in PATH - dependencies will need to be installed manually
    echo [INFO] Please navigate to the src folder and run: pip install pynput psutil
)

echo.
echo [SUCCESS] Installation completed!
echo.
echo ================================================================
echo                    INSTALLATION COMPLETE
echo ================================================================
echo.
echo Installation Summary:
echo ====================
echo Version: %version%
echo Main Directory: %main_dir%
echo Version Directory: %version_dir%
echo Source Directory: %src_dir%
echo.
echo HOW TO RUN THE PROGRAM:
echo =======================
echo.
echo STEP 1: Open File Explorer
echo STEP 2: Navigate to your Desktop
echo STEP 3: Open the folder: "DRAGEno01 RedM Panner"
echo STEP 4: Open the folder: "Python"
echo STEP 5: Double-click on: "%run_file%"
echo.
echo QUICK ACCESS:
echo =============
echo You can also copy this path and paste it into File Explorer:
echo %version_dir%
echo.
echo IMPORTANT NOTES:
echo ================
echo - Make sure you have %version% installed on your system
echo - Python dependencies (pynput, psutil) have been installed in the src folder
echo - If you encounter "module not found" errors, navigate to the src folder and run: pip install pynput psutil
echo - Check the GitHub repository for updates and support
echo.
echo GitHub Repository: https://github.com/DRAGEno01/RedM-Auto-Panning
echo.
echo ================================================================
echo.
echo Press any key to close this installer...
pause >nul

:: Function to trim spaces from variables
:trim_spaces
set "%~1=%~2"
set "%~1=!%~1: =!"
goto :eof
