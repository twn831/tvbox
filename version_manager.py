"""
TV Box Manager - Version Manager
Windows tool for managing APK version information
"""

import os
import json
import hashlib
from pathlib import Path

VERSIONS_FILE = "versions.json"
APPS_FOLDER = "apps"


def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def scan_apps_folder(folder_path):
    """Scan apps folder and return list of APKs with info"""
    apps = []
    apps_dir = Path(folder_path)

    if not apps_dir.exists():
        print(f"Error: {folder_path} does not exist!")
        return apps

    for apk_file in apps_dir.glob("*.apk"):
        info = {
            "filename": apk_file.name,
            "path": str(apk_file),
            "size": apk_file.stat().st_size,
            "hash": get_file_hash(apk_file),
        }
        apps.append(info)

    return apps


def load_versions():
    """Load existing versions file"""
    if os.path.exists(VERSIONS_FILE):
        with open(VERSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0.0", "apps": {}}


def save_versions(data):
    """Save versions file"""
    with open(VERSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_versions(apps_folder):
    """Update versions.json with current APK info"""
    print(f"Scanning {apps_folder}...")
    apps = scan_apps_folder(apps_folder)

    if not apps:
        print("No APK files found!")
        return

    data = load_versions()

    print(f"\nFound {len(apps)} APK files:\n")
    for app in apps:
        print(f"  - {app['filename']}")
        print(f"    Size: {app['size'] / 1024:.1f} KB")
        print(f"    Hash: {app['hash'][:16]}...")
        print()

        # Update or add app entry
        data["apps"][app["filename"]] = {
            "size": app["size"],
            "hash": app["hash"],
        }

    save_versions(data)
    print(f"Updated {VERSIONS_FILE}")


def check_updates(apps_folder):
    """Check which apps need updates"""
    data = load_versions()
    apps = scan_apps_folder(apps_folder)

    print("\nUpdate Status:\n")
    for app in apps:
        filename = app["filename"]
        if filename in data["apps"]:
            stored = data["apps"][filename]
            if app["hash"] == stored["hash"]:
                print(f"  [OK] {filename} - Up to date")
            else:
                print(f"  [NEW] {filename} - Updated version available")
        else:
            print(f"  [NEW] {filename} - New app")


def main():
    print("=" * 50)
    print("TV Box Manager - Version Manager")
    print("=" * 50)
    print()

    # Default to C:\APK as the apps folder
    default_path = "C:\\APK"
    apps_path = input(f"Enter apps folder path [{default_path}]: ").strip()

    if not apps_path:
        apps_path = default_path

    if not os.path.exists(apps_path):
        print(f"\nCreating {apps_path}...")
        os.makedirs(apps_path, exist_ok=True)

    while True:
        print("\n" + "=" * 50)
        print("Menu:")
        print("  1. Scan and update versions")
        print("  2. Check for updates")
        print("  3. Show current versions")
        print("  4. Exit")
        print("=" * 50)

        choice = input("\nChoice: ").strip()

        if choice == "1":
            update_versions(apps_path)
        elif choice == "2":
            check_updates(apps_path)
        elif choice == "3":
            data = load_versions()
            print(f"\nApp Version: {data['version']}")
            print(f"Apps tracked: {len(data['apps'])}")
            for name, info in data["apps"].items():
                print(f"  - {name}")
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice!")


if __name__ == "__main__":
    main()
