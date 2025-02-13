@echo off
title RedM Auto Panner Installer
color 0a

:: Create installation directory on desktop
set "INSTALL_DIR=%USERPROFILE%\Desktop\RedM Auto Panner"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Create lib directory
if not exist "%INSTALL_DIR%\lib" mkdir "%INSTALL_DIR%\lib"
if not exist "%INSTALL_DIR%\lib\src" mkdir "%INSTALL_DIR%\lib\src"

:: Download version file
curl -s https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/main/version.txt > "%INSTALL_DIR%\lib\version.txt"
set /p VERSION=<"%INSTALL_DIR%\lib\version.txt"

:: Download the main Java file
curl -s "https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/main/code/V%VERSION%/RedMPanning.java" > "%INSTALL_DIR%\lib\src\RedMPanning.java"

:: Download all required dependencies
curl -L "https://repo1.maven.org/maven2/com/1stleg/jnativehook/2.1.0/jnativehook-2.1.0.jar" > "%INSTALL_DIR%\lib\jnativehook-2.1.0.jar"

:: Create run.bat in main directory
(
echo @echo off
echo title RedM Auto Panner
echo color 0a
echo.
echo cd lib
echo.
echo :: Check if Java is installed
echo java -version ^>nul 2^>^&1
echo if %%errorlevel%% neq 0 ^(
echo     echo Java is not installed! Please install Java first.
echo     echo Press any key to exit...
echo     pause ^>nul
echo     exit /b 1
echo ^)
echo.
echo :: Compile the code
echo javac -cp "jnativehook-2.1.0.jar;src" src/RedMPanning.java
echo if %%errorlevel%% neq 0 ^(
echo     echo Compilation failed!
echo     echo Press any key to exit...
echo     pause ^>nul
echo     exit /b 1
echo ^)
echo.
echo :: Run the program
echo java -cp ".;jnativehook-2.1.0.jar;src" RedMPanning
echo.
echo exit /b 0
) > "%INSTALL_DIR%\RedM Auto Panner.bat"

:: Create README
(
echo RedM Auto Panner
echo ===============
echo.
echo Installation complete! To run the program:
echo.
echo 1. Make sure you have Java installed on your computer
echo 2. Double-click the 'RedM Auto Panner.bat' file
echo.
echo For support or issues, please visit:
echo https://github.com/DRAGEno01/RedM-Auto-Panning
echo.
echo Enjoy!
) > "%INSTALL_DIR%\README.txt"

:: Move Setup.bat to lib folder
move "%~f0" "%INSTALL_DIR%\lib\Setup.bat" >nul

echo Installation complete! The program has been installed to: %INSTALL_DIR%
echo To run the program, double-click the 'RedM Auto Panner.bat' file in the installation folder.
pause
exit
