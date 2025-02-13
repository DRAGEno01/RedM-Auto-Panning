#!/bin/bash

# Create installation directory on desktop
INSTALL_DIR="$HOME/Desktop/RedM Auto Panner"
mkdir -p "$INSTALL_DIR"

# Download the latest version file
curl -s https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/main/version.txt > "$INSTALL_DIR/version.txt"
VERSION=$(cat "$INSTALL_DIR/version.txt")

# Download the main Java file
curl -s "https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/main/code/V$VERSION/RedMPanning.java" > "$INSTALL_DIR/RedMPanning.java"

# Create Windows batch file for easy running
cat > "$INSTALL_DIR/run.bat" << 'EOF'
@echo off
title RedM Auto Panner
color 0a

:: Check if Java is installed
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo Java is not installed! Please install Java first.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Compile and run
javac RedMPanning.java
if %errorlevel% neq 0 (
    echo Compilation failed!
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

java RedMPanning
exit /b 0
EOF

# Create README file
cat > "$INSTALL_DIR/README.txt" << 'EOF'
RedM Auto Panner
===============

Installation complete! To run the program:

1. Make sure you have Java installed on your computer
2. Double-click the 'run.bat' file

For support or issues, please visit:
https://github.com/DRAGEno01/RedM-Auto-Panning

Enjoy!
EOF

# Make files executable
chmod +x "$INSTALL_DIR/run.bat"

echo "Installation complete! The program has been installed to: $INSTALL_DIR"
echo "To run the program, double-click the 'run.bat' file in the installation folder." 
