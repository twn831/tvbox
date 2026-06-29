@echo off
REM TV Box Manager - Windows Build Setup Script
REM This script helps set up the Windows environment for building the TV app

echo ========================================
echo TV Box Manager - Build Environment Setup
echo ========================================
echo.

REM Check if WSL is installed
echo [1/5] Checking WSL installation...
wsl --status >nul 2>&1
if %errorlevel% neq 0 (
    echo WSL not found. Installing WSL...
    wsl --install
    echo.
    echo Please restart your computer and run this script again.
    pause
    exit /b 1
)

REM Check if Ubuntu is installed
echo [2/5] Checking Ubuntu installation...
wsl --list | findstr /i "Ubuntu" >nul
if %errorlevel% neq 0 (
    echo Installing Ubuntu on WSL...
    wsl --install -d Ubuntu
    echo.
    echo Please restart and set up Ubuntu, then run this script again.
    pause
    exit /b 1
)

echo WSL and Ubuntu are installed.

REM Create setup script for Ubuntu
echo [3/5] Creating Ubuntu setup script...
(
echo #!/bin/bash
echo.
echo # TV Box Manager - Ubuntu Setup Script
echo # Run this once on a fresh Ubuntu WSL installation
echo.
echo set -e
echo.
echo echo "Setting up Android SDK environment..."
echo.
echo # Install system dependencies
echo sudo apt update
echo sudo apt upgrade -y
echo sudo apt install -y python3 python3-pip git unzip wget openjdk-17-jdk
echo.
echo # Set environment variables
echo export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
echo export ANDROID_HOME=/opt/android-sdk
echo export PATH=\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin:\$ANDROID_HOME/platform-tools
echo.
echo # Create Android SDK directory
echo sudo mkdir -p /opt/android-sdk
echo.
echo # Download and extract Android command line tools
echo cd /tmp
echo wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
echo sudo unzip -q commandlinetools-linux-11076708_latest.zip -d /opt/android-sdk/cmdline-tools
echo sudo mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest 2^>/dev/null ^|^| true
echo.
echo # Accept licenses
echo yes | /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
echo.
echo # Install SDK components
echo /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
echo.
echo # Install Python dependencies
echo pip3 install buildozer cython
echo.
echo echo.
echo echo "Setup complete!"
echo echo "To build the app, run:"
echo echo "  cd ~/tvbox_tv_app"
echo echo "  buildozer android debug"
) > "%TEMP%\ubuntu_setup.sh"

echo Ubuntu setup script created at %TEMP%\ubuntu_setup.sh
echo.

REM Copy setup script to Ubuntu home
echo [4/5] Copying setup script to Ubuntu...
wsl -d Ubuntu bash -c "mkdir -p ~/tvbox_tv_app 2>/dev/null || true"
copy "%TEMP%\ubuntu_setup.sh" "\\wsl$\Ubuntu\home\$(wsl -d Ubuntu bash -c 'whoami' 2>nul)\ubuntu_setup.sh" >nul 2>&1

REM Ask user to run the setup
echo [5/5] Setup instructions:
echo.
echo ============================================
echo NEXT STEPS:
echo ============================================
echo.
echo 1. Open Ubuntu terminal (type 'ubuntu' in Start menu)
echo.
echo 2. Run the setup script:
echo    bash ubuntu_setup.sh
echo.
echo 3. Copy your project files to Ubuntu:
echo    - Copy 'tvbox_tv_app' folder to ~/tvbox_tv_app
echo.
echo 4. Build the APK:
echo    cd ~/tvbox_tv_app
echo    buildozer android debug
echo.
echo ============================================
echo.
echo The APK will be created at: ~/tvbox_tv_app/bin/*.apk
echo.
pause
