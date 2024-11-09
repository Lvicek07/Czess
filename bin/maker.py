import os
import shutil
import sys
import subprocess
import PyInstaller.__main__

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
    """Attempt to locate the icon in the assets directory, or ask the user to specify it.
       If building EXE, ensure icon is .ico format."""
    icon_path = os.path.join(base_dir, "assets", "czess-icon.ico" if is_exe else "czess-icon.png")
    
    if os.path.isfile(icon_path):
        print(f"Icon found at: {icon_path}")
    else:
        print("Icon not found in the assets directory.")
        icon_path = check_file_path("Please provide the full path to the icon (e.g., czess-icon.ico or czess-icon.png): ")
    return icon_path

def build_exe(base_dir, output_dir, icon_path):
    """Build an EXE using PyInstaller's Python API."""
    print("Creating EXE for Windows...")
    try:
        PyInstaller.__main__.run([
            os.path.join(base_dir, "src/main.py"),  # Main script to bundle
            "--onefile",  # Create a single executable
            "--noconsole",  # Don't show the console window
            "--add-data", os.path.join(base_dir, "src/common.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_menu.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_client.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_server.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/local_multiplayer.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/singleplayer.py") + ":.",
            "--distpath", output_dir,  # Save the output to the `executable` directory
            "--workpath", os.path.join(output_dir, "build"),
            "--specpath", output_dir,
            "--clean", "--optimize", "2",
            "--icon", icon_path,  # Set the icon for the EXE (expecting .ico)
            "--name", "czess"  # Set the name of the EXE file
        ])
        print("EXE file has been created in the 'executable' directory.")
    except FileNotFoundError:
        print("Error: PyInstaller is not installed or not found in your PATH.")
    except Exception as e:
        print(f"Error: PyInstaller failed to create the EXE. {e}")

def build_appimage(base_dir, output_dir, linuxdeploy_path):
    """Build an AppImage for Linux."""
    print("Creating AppImage for Linux...")

    # Ensure linuxdeploy is executable
    os.chmod(linuxdeploy_path, 0o755)

    # Locate the icon
    icon_path = locate_icon(base_dir)

    # Build binary with PyInstaller
    try:
        PyInstaller.__main__.run([
            os.path.join(base_dir, "src/main.py"), "-y", "-F", "-w",
            "--add-data", os.path.join(base_dir, "src/common.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_menu.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_client.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/lan_multiplayer_server.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/local_multiplayer.py") + ":.",
            "--add-data", os.path.join(base_dir, "src/singleplayer.py") + ":.",
            "--distpath", output_dir,  # Save the output to the `executable` directory
            "--workpath", os.path.join(output_dir, "build"),
            "--specpath", output_dir,
            "--clean", "--optimize", "2"
        ])
    except FileNotFoundError:
        print("Error: PyInstaller is not installed or not found in your PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: PyInstaller failed to create the main binary. {e}")
        sys.exit(1)

    # Verify if the binary was created
    binary_path = os.path.join(output_dir, "main")
    if not os.path.isfile(binary_path):
        print("Error: PyInstaller did not create the main binary in the dist directory.")
        sys.exit(1)

    # Create AppDir structure within the output directory
    appdir_path = os.path.join(output_dir, "AppDir")
    os.makedirs(os.path.join(appdir_path, "usr/bin"), exist_ok=True)
    os.makedirs(os.path.join(appdir_path, "usr/share/applications"), exist_ok=True)
    os.makedirs(os.path.join(appdir_path, "usr/share/icons/hicolor/256x256/apps"), exist_ok=True)

    # Move binary to AppDir
    shutil.move(binary_path, os.path.join(appdir_path, "usr/bin/main"))

    # Create .desktop file
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

    # Add icon to AppDir
    shutil.copy(icon_path, os.path.join(appdir_path, "usr/share/icons/hicolor/256x256/apps/czess-icon.png"))

    # Run linuxdeploy to create the AppImage
    try:
        subprocess.check_call([linuxdeploy_path, "--appdir", appdir_path, "--output", "appimage", "--output", output_dir])
        print("AppImage has been created successfully in the 'executable' directory.")
    except subprocess.CalledProcessError:
        print("Error: linuxdeploy failed to create the AppImage.")
        sys.exit(1)

def main():
    # Ask user for the base directory containing the czess project files
    base_dir = get_valid_directory("Please enter the parent directory of the czess project: ")

    # Create an 'executable' directory within the base directory
    output_dir = os.path.join(base_dir, "executable")
    os.makedirs(output_dir, exist_ok=True)

    # Locate the icon (check for .ico for EXE)
    icon_path = locate_icon(base_dir, is_exe=True)

    # Prompt the user to choose between EXE and AppImage
    choice = input("Do you want to create an EXE (Windows) or AppImage (Linux)? Type 'exe' or 'appimage': ").strip().lower()

    if choice == "exe":
        build_exe(base_dir, output_dir, icon_path)
    elif choice == "appimage":
        # Prompt for the path to linuxdeploy
        linuxdeploy_path = check_file_path("Please enter the full path to linuxdeploy (e.g., linuxdeploy-x86_64.AppImage): ")
        build_appimage(base_dir, output_dir, linuxdeploy_path)
    else:
        print("Invalid choice. Please run the script again and enter 'exe' or 'appimage'.")

if __name__ == "__main__":
    main()
