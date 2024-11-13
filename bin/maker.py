import os
import shutil
import subprocess
import PyInstaller.__main__
import platform

def get_base_dir():
    """Return the base directory one level up from the 'bin' directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, '..'))
    
    if os.path.isdir(os.path.join(base_dir, "bin")) and os.path.isdir(os.path.join(base_dir, "src")) and os.path.isdir(os.path.join(base_dir, "assets")):
        print(f"Base directory found: {base_dir}")
        return base_dir
    else:
        print("Error: Could not find the expected structure in the base directory.")
        return get_valid_directory("Please enter the correct base directory path: ")

def get_valid_directory(prompt):
    """Prompt the user to enter a directory path and validate it."""
    path = input(prompt).strip()
    while not os.path.isdir(path):
        print(f"Invalid directory: {path}")
        path = input("Please enter a valid directory path: ").strip()
    return path

def check_file_path(prompt):
    """Prompt the user to enter a file path and validate it."""
    path = input(prompt).strip()
    while not os.path.isfile(path):
        print(f"Invalid file path: {path}")
        path = input("Please enter a valid file path: ").strip()
    return path

def locate_icon(base_dir, is_exe=False):
    """Locate the icon in the assets directory or ask the user to specify it.
       If building EXE, ensure icon is .ico format."""
    icon_path = os.path.join(base_dir, "assets", "czess-icon.ico" if is_exe else "czess-icon.png")
    
    if os.path.isfile(icon_path):
        print(f"Icon found at: {icon_path}")
    else:
        print("Icon not found in the assets directory.")
        icon_path = check_file_path("Please provide the full path to the icon (e.g., czess-icon.ico or czess-icon.png): ")
    return icon_path

def locate_linuxdeploy(base_dir):
    """Locate linuxdeploy in the bin directory or ask the user to specify it."""
    linuxdeploy_path = os.path.join(base_dir, "bin", "linuxdeploy-x86_64.AppImage")
    
    if os.path.isfile(linuxdeploy_path):
        print(f"linuxdeploy found at: {linuxdeploy_path}")
    else:
        print("linuxdeploy not found in the bin directory.")
        linuxdeploy_path = check_file_path("Please provide the full path to linuxdeploy (e.g., linuxdeploy-x86_64.AppImage): ")
    
    return linuxdeploy_path

def build_exe(base_dir, icon_path):
    """Build an EXE using PyInstaller's Python API."""
    executable_dir = os.path.join(base_dir, "executable")  # Output EXE in the 'executable' folder
    
    if not os.path.exists(executable_dir):
        os.makedirs(executable_dir)  # Create 'executable' directory if it doesn't exist
    
    print("Creating EXE for Windows...")
    try:
        PyInstaller.__main__.run([
            os.path.join(base_dir, "src/main.py"),
            "--onefile",
            "--noconsole",
            "--add-data", os.path.join(base_dir, "src/common.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_menu.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_client.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_server.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/local_multiplayer.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/singleplayer.py") + ":.",
            "--distpath", executable_dir,
            "--workpath", os.path.join(executable_dir, "build"),
            "--specpath", executable_dir,
            "--clean", "--optimize", "2",
            "--icon", icon_path,
            "--name", "czess",
            "--log-level", "DEBUG"
        ])
        print(f"EXE file has been created and saved in: {executable_dir}")
    except Exception as e:
        print(f"Error: PyInstaller failed to create the EXE. {e}")

def build_appimage(base_dir, linuxdeploy_path):
    """Build an AppImage for Linux."""
    executable_dir = os.path.join(base_dir, "executable")  # Output AppImage in the 'executable' folder
    
    if not os.path.exists(executable_dir):
        os.makedirs(executable_dir)  # Create 'executable' directory if it doesn't exist

    print("Creating AppImage for Linux...")

    # Ensure linuxdeploy has execution permissions
    os.chmod(linuxdeploy_path, 0o755)

    icon_path = locate_icon(base_dir)

    try:
        # Create the main binary using PyInstaller
        PyInstaller.__main__.run([
            os.path.join(base_dir, "src/main.py"), "-y", "-F", "-w",
            "--add-data", os.path.join(base_dir, "src/common.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_menu.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_client.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_server.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/local_multiplayer.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/singleplayer.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/capture.mp3") + ":.",
            "--add-data", os.path.join(base_dir, "src/move-sound.mp3") + ":.",
            "--distpath", executable_dir,
            "--workpath", os.path.join(executable_dir, "build"),
            "--specpath", executable_dir,
            "--clean", "--optimize", "2"
        ])
    except Exception as e:
        print(f"Error: PyInstaller failed to create the main binary. {e}")
        return

    # Check if the binary was created
    binary_path = os.path.join(executable_dir, "main")
    if not os.path.isfile(binary_path):
        print("Error: PyInstaller did not create the main binary.")
        return

    # Set up the AppDir structure
    appdir_path = os.path.join(executable_dir, "AppDir")
    os.makedirs(os.path.join(appdir_path, "usr/bin"), exist_ok=True)
    os.makedirs(os.path.join(appdir_path, "usr/share/applications"), exist_ok=True)
    os.makedirs(os.path.join(appdir_path, "usr/share/icons/hicolor/256x256/apps"), exist_ok=True)

    # Move the binary to AppDir
    shutil.move(binary_path, os.path.join(appdir_path, "usr/bin/main"))

    # Create the desktop entry
    desktop_content = """[Desktop Entry]
Version=1.0
Name=Czess
Comment=Chess on Python
Exec=main
Icon=czess-icon
Terminal=false
Type=Application
Categories=Game;
"""
    with open(os.path.join(appdir_path, "usr/share/applications/czess.desktop"), "w") as f:
        f.write(desktop_content)

    # Copy the icon to the AppDir
    shutil.copy(icon_path, os.path.join(appdir_path, "usr/share/icons/hicolor/256x256/apps/czess-icon.png"))

    try:
        # Debugging: Print output dir and final path
        print(f"Output directory: {executable_dir}")
        print(f"AppDir path: {appdir_path}")

        # Create the AppImage using linuxdeploy
        subprocess.check_call([linuxdeploy_path, "--appdir", appdir_path, "--output", "appimage"])
        print(f"AppImage has been created successfully and saved in: {executable_dir}")
    except subprocess.CalledProcessError:
        print("Error: linuxdeploy failed to create the AppImage.")

def main():
    base_dir = get_base_dir()
    
    icon_path = locate_icon(base_dir, is_exe=True)

    system = platform.system()

    if system == "Linux":
        linuxdeploy_path = locate_linuxdeploy(base_dir)
        build_appimage(base_dir, linuxdeploy_path)
    elif system == "Windows":
        build_exe(base_dir, icon_path)
    else:
        print("Cannot determine OS type")
        choice = input("Do you want to create an EXE (Windows) or AppImage (Linux)? Type 'exe' or 'appimage': ").strip().lower()

        if choice == "exe":
            build_exe(base_dir, icon_path)
        elif choice == "appimage":
            linuxdeploy_path = locate_linuxdeploy(base_dir)
            build_appimage(base_dir, linuxdeploy_path)
        else:
            print("Invalid choice. Please run the script again and enter 'exe' or 'appimage'.")

if __name__ == "__main__":
    main()
