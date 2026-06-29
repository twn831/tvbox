# TV Box Manager

A simple Android TV application to manage and install apps from USB storage.

## Features

- **USB Detection**: Automatically detects USB storage connected to Android TV
- **App List**: Displays all APK files found in the `/apps` folder on USB
- **One-Click Install**: Install all apps with a single button press
- **Update Detection**: Shows which apps are already installed

## USB Structure

Place your APK files in this structure:

```
USB Drive/
└── apps/
    ├── app1.apk
    ├── app2.apk
    └── app3.apk
```

## Building

### Requirements

- Windows 10/11 with WSL (Windows Subsystem for Linux)
- Ubuntu on WSL
- Java JDK 17
- Android SDK
- Buildozer

### Quick Build

1. Open Ubuntu terminal
2. Navigate to project folder
3. Run: `buildozer android debug`
4. Find APK in `bin/` folder

### First-Time Setup

If this is your first time building, run `setup_windows.bat` on Windows to set up the build environment.

For detailed instructions, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md).

## Installation

1. Copy the APK to a USB drive
2. Open the file manager on your Android TV
3. Navigate to USB drive
4. Click on the APK to install

Or use ADB:

```bash
adb install tvboxmanager-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

## Project Structure

```
tvbox_tv_app/
├── main.py              # Main application code
├── tvbox.kv             # Kivy UI layout
├── buildozer.spec       # Build configuration
├── BUILD_INSTRUCTIONS.md # Detailed build guide
├── setup_windows.bat    # Windows setup script
└── README.md            # This file
```

## Development

The app is built with Kivy, a Python framework for developing touch applications.

### Key Files

- `main.py`: Contains all the business logic
- `tvbox.kv`: Defines the UI layout (TV-friendly, large fonts, D-pad navigation)

### Customization

To change the apps folder name, edit `APPS_FOLDER` in `main.py`.

## License

MIT License
