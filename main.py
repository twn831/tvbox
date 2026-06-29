"""
TV Box Manager - Kivy Application
A simple app to manage and install apps from USB/storage on Android TV and Phone
Supports both TV mode and phone mode (Origin OS compatible)
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path

# Try to import Kivy, handle gracefully if not available
try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.popup import Popup
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.textinput import TextInput
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.properties import StringProperty, ListProperty, BooleanProperty
    from kivy.storage.jsonstore import JsonStore
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False
    # Mock classes for when running on Windows (development)
    class MockProperty:
        def __init__(self, default=None):
            self.default = default
        def __get__(self, obj, objtype=None):
            return self.default
        def __set__(self, obj, value):
            pass

    class MockWidget:
        pass

    class Screen:
        name = ""
        def __init__(self, **kwargs):
            pass

    class App:
        pass

# ============================================================
# Device Detection
# ============================================================

def is_android_tv():
    """Detect if running on Android TV"""
    try:
        # Check for TV-related system properties
        result = subprocess.run(
            ['getprop', 'ro.product.model'],
            capture_output=True,
            text=True,
            timeout=5
        )
        model = result.stdout.lower()
        if 'tv' in model or 'box' in model or 'stick' in model:
            return True

        # Check for TV UI mode
        result = subprocess.run(
            ['getprop', 'ro.build.characteristics'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'tv' in result.stdout.lower():
            return True

        # Check for Leanback launcher
        result = subprocess.run(
            ['pm', 'list', 'packages', 'android.leanback.launcher'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True

    except Exception:
        pass
    return False


def is_phone():
    """Detect if running on a phone (not TV)"""
    return not is_android_tv()


# Device type cache
DEVICE_IS_TV = None


def get_device_type():
    """Get cached device type"""
    global DEVICE_IS_TV
    if DEVICE_IS_TV is None:
        DEVICE_IS_TV = is_android_tv()
    return DEVICE_IS_TV


# ============================================================
# Storage Paths
# ============================================================

# TV USB paths
TV_USB_PATHS = [
    "/storage/usbhost0",
    "/storage/usbhost1",
    "/storage/usbhost2",
    "/mnt/usb0",
    "/mnt/usb1",
    "/external_usb",
]

# Phone storage paths (Origin OS and general Android)
PHONE_STORAGE_PATHS = [
    "/storage/usb0",       # Origin OS USB OTG
    "/storage/udisk0",     # Alternative Origin OS USB
    "/storage/sdcard0",    # Phone internal storage
    "/storage/emulated/0", # Android internal storage
    "/sdcard",             # Symlink to internal storage
    "/storage/emulated/0/Download",  # Download folder
    "/storage/emulated/0/DCIM",      # Camera folder
]

# Combined search paths
ALL_STORAGE_PATHS = TV_USB_PATHS + PHONE_STORAGE_PATHS

# Apps folder name
APPS_FOLDER = "apps"


def find_storage_path():
    """
    Find available storage path.
    Priority: USB (TV) > Phone storage
    Returns (path, storage_type) tuple
    """
    # First try TV USB paths
    for path in TV_USB_PATHS:
        if os.path.exists(path):
            return path, "usb"

    # Then try phone storage paths
    for path in PHONE_STORAGE_PATHS:
        if os.path.exists(path):
            return path, "phone"

    return None, None


def get_all_storage_locations():
    """Get all available storage locations for browsing"""
    locations = []

    # USB drives (TV)
    for path in TV_USB_PATHS:
        if os.path.exists(path):
            try:
                label = get_storage_label(path)
                locations.append({
                    'path': path,
                    'type': 'usb',
                    'label': label or path,
                    'icon': 'sd'
                })
            except:
                pass

    # Phone storage paths
    for path in PHONE_STORAGE_PATHS:
        if os.path.exists(path):
            try:
                label = get_storage_label(path)
                if path == "/storage/emulated/0" or path == "/sdcard":
                    label = "Internal Storage"
                elif path == "/storage/usb0":
                    label = "USB OTG"
                elif path == "/storage/udisk0":
                    label = "USB Drive"
                locations.append({
                    'path': path,
                    'type': 'phone',
                    'label': label or path,
                    'icon': 'folder'
                })
            except:
                pass

    return locations


def get_storage_label(path):
    """Try to get storage label from mount point"""
    try:
        # Read /proc/mounts to get mount info
        with open('/proc/mounts', 'r') as f:
            for line in f:
                if path in line:
                    parts = line.split()
                    if len(parts) > 0:
                        return parts[1].split('/')[-1]
    except:
        pass
    return None


def list_directories(path):
    """List directories in a path"""
    dirs = []
    try:
        if os.path.exists(path) and os.path.isdir(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    dirs.append(item)
    except PermissionError:
        pass
    return sorted(dirs)


# ============================================================
# APK Functions
# ============================================================

def get_apps_from_folder(folder_path, scan_subdirs=False):
    """Get list of APK files from a folder"""
    apps = []
    if folder_path and os.path.exists(folder_path):
        try:
            for file in os.listdir(folder_path):
                if file.endswith('.apk'):
                    file_path = os.path.join(folder_path, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        apps.append({
                            'name': file[:-4],  # Remove .apk extension
                            'filename': file,
                            'path': file_path,
                            'size': file_size
                        })
                    except:
                        pass

            # Optionally scan subdirectories
            if scan_subdirs:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isdir(item_path):
                        apps.extend(get_apps_from_folder(item_path, scan_subdirs=False))

        except PermissionError:
            pass
    return apps


def get_apps_from_usb(usb_path, scan_subdirs=True):
    """Get list of APK files from USB apps folder"""
    apps_folder = os.path.join(usb_path, APPS_FOLDER)
    if os.path.exists(apps_folder):
        return get_apps_from_folder(apps_folder, scan_subdirs)
    # If no apps folder, scan the root
    return get_apps_from_folder(usb_path, scan_subdirs=False)


def get_installed_apps():
    """Get list of installed apps on the device"""
    try:
        result = subprocess.run(
            ['pm', 'list', 'packages', '-3'],
            capture_output=True,
            text=True,
            timeout=30
        )
        apps = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                pkg_name = line.replace('package:', '').strip()
                apps.append(pkg_name)
        return apps
    except Exception as e:
        return []


def install_apk(apk_path, callback=None):
    """Install an APK file"""
    try:
        result = subprocess.run(
            ['pm', 'install', '-r', apk_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        success = result.returncode == 0
        if callback:
            callback(success, result.stdout, result.stderr)
        return success
    except Exception as e:
        if callback:
            callback(False, '', str(e))
        return False


def check_app_update(apk_name, installed_apps):
    """Check if an app needs update"""
    pkg_name = apk_name.lower().replace(' ', '.').replace('-', '.')
    for installed in installed_apps:
        if pkg_name in installed.lower() or installed.lower() in pkg_name:
            return True, installed
    return False, None


# ============================================================
# Kivy UI Classes
# ============================================================

if KIVY_AVAILABLE:
    class AppListItem(BoxLayout):
        """Single app item in the list"""
        app_name = StringProperty()
        app_size = StringProperty()
        app_status = StringProperty()

        def __init__(self, app_info, **kwargs):
            super().__init__(**kwargs)
            self.app_info = app_info
            self.app_name = app_info['name']
            self.app_size = self.format_size(app_info['size'])
            self.app_status = ""

        def format_size(self, size):
            """Format file size to human readable"""
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"


    class StorageLocationItem(BoxLayout):
        """Storage location item for browsing"""
        location_path = StringProperty()
        location_label = StringProperty()
        location_type = StringProperty()

        def __init__(self, location_info, **kwargs):
            super().__init__(**kwargs)
            self.location_info = location_info
            self.location_path = location_info['path']
            self.location_label = location_info.get('label', location_info['path'])
            self.location_type = location_info.get('type', 'unknown')


    class MainScreen(Screen):
        """Main screen with app list"""
        usb_path = StringProperty("")
        storage_type = StringProperty("")
        apps = ListProperty([])
        current_folder = StringProperty("")
        available_locations = ListProperty([])
        is_phone_mode = BooleanProperty(False)

        def on_enter(self):
            """Called when screen is entered"""
            self.is_phone_mode = get_device_type() == False  # Not TV
            self.refresh_storages()

        def refresh_storages(self):
            """Refresh available storage locations"""
            self.available_locations = get_all_storage_locations()
            self.refresh_apps()

        def refresh_apps(self, folder_path=None):
            """Refresh the app list from current or specified folder"""
            if folder_path:
                self.current_folder = folder_path
                self.apps = get_apps_from_folder(folder_path)
            else:
                # Try to find storage path
                storage_path, storage_type = find_storage_path()
                self.usb_path = storage_path
                self.storage_type = storage_type

                if storage_path:
                    self.current_folder = storage_path
                    self.apps = get_apps_from_usb(storage_path)
                else:
                    self.current_folder = ""
                    self.apps = []

            self.update_ui()

        def update_ui(self):
            """Update the app list UI"""
            self.ids.app_list.clear_widgets()

            if self.apps:
                for app in self.apps:
                    self.ids.app_list.add_widget(AppListItem(app))
            else:
                # No apps found - show appropriate message
                if self.current_folder:
                    no_apps_label = Label(
                        text="[color=ffaa00]No APK files found in current folder[/color]\n\n"
                             "Current: " + self.current_folder + "\n\n"
                             "Try browsing to another location or\n"
                             "check if your APK files are in a subfolder",
                        markup=True,
                        halign='center',
                        valign='middle',
                        font_size='18sp'
                    )
                else:
                    no_apps_label = Label(
                        text="[color=ff6666]No storage found![/color]\n\n"
                             "Please connect USB drive or\n"
                             "browse to internal storage",
                        markup=True,
                        halign='center',
                        valign='middle',
                        font_size='20sp'
                    )
                self.ids.app_list.add_widget(no_apps_label)

        def browse_folder(self):
            """Open folder browser popup"""
            if not self.available_locations:
                self.available_locations = get_all_storage_locations()

            content = BoxLayout(orientation='vertical', padding=10, spacing=10)

            # Storage location list
            loc_label = Label(
                text='[b]Select Storage Location:[/b]',
                markup=True,
                size_hint_y=0.15,
                font_size='18sp'
            )
            content.add_widget(loc_label)

            scroll = ScrollView(size_hint_y=0.5)
            loc_layout = GridLayout(cols=1, size_hint_y=None, spacing=5)
            loc_layout.bind(minimum_height=loc_layout.setter('height'))

            for loc in self.available_locations:
                btn = Button(
                    text=f"{loc.get('label', loc['path'])} ({loc['type']})",
                    size_hint_y=None,
                    height='50sp',
                    font_size='16sp'
                )
                btn.location = loc
                btn.bind(on_press=self.on_location_selected)
                loc_layout.add_widget(btn)

            scroll.add_widget(loc_layout)
            content.add_widget(scroll)

            # Custom path input
            path_box = BoxLayout(size_hint_y=0.2, spacing=10)
            path_box.add_widget(Label(text='Custom path:', font_size='14sp'))
            custom_path = TextInput(
                hint_text='/storage/emulated/0/Download',
                multiline=False,
                font_size='14sp'
            )
            path_box.add_widget(custom_path)
            content.add_widget(path_box)

            # Buttons
            btn_box = BoxLayout(size_hint_y=0.15, spacing=10)
            close_btn = Button(text='Close', font_size='16sp')
            browse_btn = Button(text='Browse Custom Path', font_size='16sp')

            def close_popup(btn):
                popup.dismiss()

            def browse_custom(btn):
                if custom_path.text.strip():
                    self.refresh_apps(custom_path.text.strip())
                popup.dismiss()

            close_btn.bind(on_press=close_popup)
            browse_btn.bind(on_press=browse_custom)
            btn_box.add_widget(close_btn)
            btn_box.add_widget(browse_btn)
            content.add_widget(btn_box)

            popup = Popup(
                title='Browse Storage Locations',
                content=content,
                size_hint=(0.9, 0.8)
            )
            popup.open()

        def on_location_selected(self, btn):
            """Handle storage location selection"""
            loc = btn.location
            self.refresh_apps(loc['path'])
            # Dismiss parent popup
            for widget in App.get_running_app().root.children:
                if hasattr(widget, 'dismiss'):
                    try:
                        widget.dismiss()
                    except:
                        pass


    class InstallScreen(Screen):
        """Screen for installing apps"""
        current_app = StringProperty("")
        install_status = StringProperty("")
        source_folder = StringProperty("")

        def install_all(self):
            """Install all apps from current storage"""
            storage_path, _ = find_storage_path()
            if not storage_path:
                storage_path = self.source_folder

            if not storage_path:
                self.install_status = "Storage not found!"
                return

            # Try apps folder first, then root
            apps_folder = os.path.join(storage_path, APPS_FOLDER)
            if os.path.exists(apps_folder):
                install_path = apps_folder
            else:
                install_path = storage_path

            if not os.path.exists(install_path):
                self.install_status = "Apps folder not found!"
                return

            success_count = 0
            fail_count = 0
            apps = get_apps_from_folder(install_path)

            if not apps:
                self.install_status = "No APK files found!"
                return

            for app in apps:
                apk_path = app['path']
                self.current_app = f"Installing: {app['filename']}"
                if install_apk(apk_path):
                    success_count += 1
                else:
                    fail_count += 1

            self.install_status = f"Complete!\nSuccess: {success_count}\nFailed: {fail_count}"

        def install_single(self, apk_path):
            """Install a single APK"""
            self.current_app = f"Installing: {os.path.basename(apk_path)}"
            if install_apk(apk_path):
                self.install_status = "Installation successful!"
            else:
                self.install_status = "Installation failed!"


    class InstalledAppsScreen(Screen):
        """Screen showing installed apps"""
        installed_apps = ListProperty([])

        def on_enter(self):
            """Called when screen is entered"""
            self.load_installed_apps()

        def load_installed_apps(self):
            """Load and display installed apps"""
            apps = get_installed_apps()
            self.installed_apps = sorted(apps)


    class SettingsScreen(Screen):
        """Settings screen"""
        apps_folder = StringProperty(APPS_FOLDER)
        device_type = StringProperty("")
        storage_locations = ListProperty([])

        def on_enter(self):
            """Update settings display"""
            self.device_type = "Android TV" if get_device_type() else "Phone/Tablet"
            self.storage_locations = get_all_storage_locations()


    class TVBoxApp(App):
        """Main TV Box Manager App"""

        def build(self):
            """Build the application"""
            is_tv = get_device_type()

            # Set window properties based on device type
            if is_tv:
                # TV mode: fullscreen
                Window.fullscreen = 'auto'
                Window.borderless = True
            else:
                # Phone mode: normal window
                Window.fullscreen = False
                Window.borderless = False
                Window.size = (400, 700)  # Phone-like dimensions

            # Create screen manager
            sm = ScreenManager()

            # Add screens
            sm.add_widget(MainScreen(name='main'))
            sm.add_widget(InstallScreen(name='install'))
            sm.add_widget(InstalledAppsScreen(name='installed'))
            sm.add_widget(SettingsScreen(name='settings'))

            return sm

        def on_start(self):
            """Called when app starts"""
            pass

        def on_pause(self):
            """Called when app is paused"""
            return True

        def on_resume(self):
            """Called when app resumes"""
            pass


def main():
    """Main entry point"""
    if KIVY_AVAILABLE:
        TVBoxApp().run()
    else:
        print("Kivy not available. This module needs to run on Android.")
        print("Please build the APK using Buildozer.")


if __name__ == '__main__':
    main()
