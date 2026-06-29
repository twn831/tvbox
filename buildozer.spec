[app]
title = TV Box Manager
package.name = tvboxmanager
package.domain = com.tvbox
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.1.0
requirements = python3,kivy

# Bootstrap configuration - CRITICAL for proper Python compilation
bootstrap = sdl2

# Support both portrait (phone) and landscape (TV)
orientation = all
fullscreen = 0
android.archs = armeabi-v7a, arm64-v8a
android.allow_backup = True

# P4A configuration
p4a.bootstrap = sdl2
p4aSDL2_kivy_version = 2.2.0

# Permissions for storage access and APK installation
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INSTALL_PACKAGES,MANAGE_EXTERNAL_STORAGE,REQUEST_INSTALL_PACKAGES
android.minapi = 21
android.api = 34
android.disable_pygame_cursor = 1

# Window settings - let app decide based on device type
android.entrypoint = main.py

# Log level
log_level = 2
