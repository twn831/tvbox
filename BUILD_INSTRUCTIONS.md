# TV Box Manager - Build Instructions

## Prerequisites

1. **WSL (Windows Subsystem for Linux)** - Required for building APK
2. **Ubuntu on WSL** - The Linux distribution for build environment

## Quick Setup (Run these commands in WSL Ubuntu)

### 1. Install Ubuntu (if not already installed)

```bash
wsl --install -d Ubuntu
```

### 2. Update Ubuntu and install dependencies

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip git unzip
```

### 3. Install Java JDK 17

```bash
sudo apt install -y openjdk-17-jdk
```

### 4. Set environment variables

Add these to your `~/.bashrc`:

```bash
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export ANDROID_HOME=/opt/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

### 5. Install Android SDK

```bash
cd /tmp
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
sudo mkdir -p /opt/android-sdk/cmdline-tools
sudo unzip commandlinetools-linux-11076708_latest.zip
sudo mv cmdline-tools /opt/android-sdk/cmdline-tools/latest
```

Accept licenses:
```bash
yes | /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
```

Install SDK components:
```bash
/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
```

### 6. Install Buildozer and dependencies

```bash
pip3 install buildozer cython
```

### 7. Clone and build your project

```bash
cd ~
git clone <your-repo-url>
cd tvbox_tv_app
buildozer android debug
```

The APK will be in `bin/` directory.

## Updating the App

1. Make changes to `main.py` or `tvbox.kv`
2. Commit changes to git
3. On your build machine (WSL), pull changes
4. Run `buildozer android debug` to rebuild

## Building Release APK

```bash
buildozer android release
```

You'll need to sign the APK for distribution.
