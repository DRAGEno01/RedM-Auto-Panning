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

:: Check which versions are supported
echo [INFO] Checking which versions are supported...

:: Check Python support
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

:: Check Java support
echo [INFO] Checking Java version support...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Java/info.txt' -TimeoutSec 10; $content = $response.Content; Write-Output $content } catch { Write-Output 'ERROR: Failed to fetch Java version info' }" > temp_java_info.txt

set "java_supported="
set "java_version="
if exist temp_java_info.txt (
    for /f "usebackq delims=" %%a in ("temp_java_info.txt") do (
        echo %%a | findstr /r "supported.*=" >nul && (
            for /f "tokens=2 delims==" %%b in ("%%a") do (
                set "temp_value=%%b"
                call :trim_spaces java_supported "%%temp_value%%"
            )
        )
        echo %%a | findstr /r "version.*=" >nul && (
            for /f "tokens=2 delims==" %%b in ("%%a") do (
                set "temp_value=%%b"
                call :trim_spaces java_version "%%temp_value%%"
            )
        )
    )
    del temp_java_info.txt
)

:: Check if any versions are supported
if "%python_supported%"=="false" if "%java_supported%"=="false" (
    echo [ERROR] No supported versions available
    echo [INFO] Please visit: https://github.com/DRAGEno01/RedM-Auto-Panning/releases
    echo [INFO] to download a supported version
    pause
    exit /b 1
)

:: Build menu based on supported versions
set "option_count=0"

if not "%python_supported%"=="false" (
    set /a option_count+=1
    set "python_option=%option_count%"
)

if not "%java_supported%"=="false" (
    set /a option_count+=1
    set "java_option=%option_count%"
)

:: Show menu
echo Please select which version you would like to install:
echo.

if not "%python_supported%"=="false" (
    echo [%python_option%] Python Version
    if "%python_version%" neq "" echo     Version: %python_version%
)

if not "%java_supported%"=="false" (
    echo [%java_option%] Java Version
    if "%java_version%" neq "" echo     Version: %java_version%
)

echo.
set /p choice="Enter your choice: "

:: Process user choice
set "version="
set "info_url="
set "main_file="
set "requirements_file="
set "setup_file="
set "run_file="

if "%choice%"=="%python_option%" if not "%python_supported%"=="false" (
    set "version=Python"
    set "info_url=https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/info.txt"
    set "main_file=RedMPanning.py"
    set "requirements_file=requirements.txt"
    set "setup_file=Setup.bat"
    set "run_file=RedM Auto Panner.bat"
    set "version_number=%python_version%"
) else if "%choice%"=="%java_option%" if not "%java_supported%"=="false" (
    set "version=Java"
    set "info_url=https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Java/info.txt"
    set "main_file=RedMPanning.java"
    set "requirements_file=jnativehook-2.1.0.jar"
    set "setup_file=Setup.bat"
    set "run_file=RedM Auto Panner.bat"
    set "version_number=%java_version%"
) else (
    echo [ERROR] Invalid choice. Please run the installer again.
    pause
    exit /b 1
)

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
if "%version%"=="Python" (
    if "%version_number%"=="" (
        echo [WARNING] Version number is empty, trying fallback URL...
        powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/lib/src/%main_file%' -OutFile '%src_dir%\%main_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %main_file%' } catch { Write-Output 'ERROR: Failed to download %main_file%' }"
    ) else (
        powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/V%version_number%/%main_file%' -OutFile '%src_dir%\%main_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %main_file%' } catch { Write-Output 'ERROR: Failed to download %main_file%' }"
    )
) else if "%version%"=="Java" (
    if "%version_number%"=="" (
        echo [WARNING] Version number is empty, trying fallback URL...
        powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Java/lib/src/%main_file%' -OutFile '%src_dir%\%main_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %main_file%' } catch { Write-Output 'ERROR: Failed to download %main_file%' }"
    ) else (
        powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Java/V%version_number%/%main_file%' -OutFile '%src_dir%\%main_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %main_file%' } catch { Write-Output 'ERROR: Failed to download %main_file%' }"
    )
)

if not exist "%src_dir%\%main_file%" (
    echo [ERROR] Failed to download %main_file%
    pause
    exit /b 1
)

:: Download requirements file
echo [INFO] Downloading %requirements_file%...
if "%version%"=="Python" (
    powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/%requirements_file%' -OutFile '%src_dir%\%requirements_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %requirements_file%' } catch { Write-Output 'WARNING: Failed to download %requirements_file%' }"
) else if "%version%"=="Java" (
    powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Java/lib/%requirements_file%' -OutFile '%src_dir%\lib\%requirements_file%' -TimeoutSec 30; Write-Output 'SUCCESS: Downloaded %requirements_file%' } catch { Write-Output 'WARNING: Failed to download %requirements_file%' }"
)

:: Note: Setup.bat files are not available in the repository

:: Create run script
echo [INFO] Creating run script...
if "%version%"=="Python" (
    echo @echo off > "%version_dir%\%run_file%"
    echo cd /d "%%~dp0" >> "%version_dir%\%run_file%"
    echo if not exist "src\%main_file%" ^( >> "%version_dir%\%run_file%"
    echo     echo [ERROR] Main file not found. Please run the installer first. >> "%version_dir%\%run_file%"
    echo     echo [INFO] To download the installer, visit: https://github.com/DRAGEno01/RedM-Auto-Panning/releases >> "%version_dir%\%run_file%"
    echo     pause >> "%version_dir%\%run_file%"
    echo     exit /b 1 >> "%version_dir%\%run_file%"
    echo ^) >> "%version_dir%\%run_file%"
    echo cd src >> "%version_dir%\%run_file%"
    echo start /min pythonw %main_file% >> "%version_dir%\%run_file%"
    echo exit >> "%version_dir%\%run_file%"
) else if "%version%"=="Java" (
    echo @echo off > "%version_dir%\%run_file%"
    echo cd /d "%%~dp0" >> "%version_dir%\%run_file%"
    echo echo [INFO] Starting RedM Auto Panning - Java Version >> "%version_dir%\%run_file%"
    echo echo. >> "%version_dir%\%run_file%"
    echo if not exist "src\%main_file%" ^( >> "%version_dir%\%run_file%"
    echo     echo [ERROR] Main file not found. Please run Setup.bat first. >> "%version_dir%\%run_file%"
    echo     pause >> "%version_dir%\%run_file%"
    echo     exit /b 1 >> "%version_dir%\%run_file%"
    echo ^) >> "%version_dir%\%run_file%"
    echo cd src >> "%version_dir%\%run_file%"
    echo javac -cp "lib\jnativehook-2.1.0.jar" %main_file% >> "%version_dir%\%run_file%"
    echo if %%errorLevel%% neq 0 ^( >> "%version_dir%\%run_file%"
    echo     echo [ERROR] Compilation failed. Please check Java installation. >> "%version_dir%\%run_file%"
    echo     pause >> "%version_dir%\%run_file%"
    echo     exit /b 1 >> "%version_dir%\%run_file%"
    echo ^) >> "%version_dir%\%run_file%"
    echo java -cp ".;lib\jnativehook-2.1.0.jar" RedMPanning >> "%version_dir%\%run_file%"
    echo pause >> "%version_dir%\%run_file%"
)

echo [SUCCESS] Created run script: %version_dir%\%run_file%

:: Create lib directory for Java if needed
if "%version%"=="Java" (
    if not exist "%src_dir%\lib" mkdir "%src_dir%\lib"
)

:: Run setup for Python to install dependencies in src folder
if "%version%"=="Python" (
    echo.
    echo [INFO] Installing Python dependencies in src folder...
    echo [INFO] This may take a few moments...
    
    :: Check if Python is available
    python --version >nul 2>&1
    if %errorLevel% == 0 (
        echo [INFO] Python is available, installing dependencies...
        
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
echo STEP 4: Open the folder: "%version%"
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
if "%version%"=="Python" (
    echo - Python dependencies (pynput, psutil) have been installed in the src folder
    echo - If you encounter "module not found" errors, navigate to the src folder and run: pip install pynput psutil
) else (
    echo - If you encounter issues, make sure Java is properly installed
)
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
