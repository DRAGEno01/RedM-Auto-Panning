#!/bin/bash

# Download Setup.bat
echo "Downloading RedM Auto Panner installer..."
curl -L -o Setup.bat https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/main/Setup.bat

# Make it executable and run
echo "Starting installation..."
chmod +x Setup.bat
./Setup.bat

# Clean up the downloaded Setup.bat after installation
rm Setup.bat 
