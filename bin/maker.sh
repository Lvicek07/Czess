#!/bin/bash

# Funkce pro kontrolu, zda soubor existuje v adresáři, pokud ne, požádá o jeho cestu
ask_for_file_in_directory() {
    directory=$1
    filename=$2

    # Pokud soubor není v adresáři, požádat o jeho cestu
    if [ ! -f "$directory/$filename" ]; then
        echo "Soubor $filename nebyl nalezen v adresáři $directory."
        echo "Zadejte plnou cestu k souboru $filename:"
        read path
        if [ -f "$path" ]; then
            echo "Soubor $filename bude použit z: $path"
            eval "$filename=$path"
        else
            echo "Soubor $path neexistuje. Zkuste to znovu."
            ask_for_file_in_directory "$directory" "$filename"
        fi
    else
        echo "Soubor $filename nalezen v adresáři $directory."
        eval "$filename=$directory/$filename"
    fi
}

# Zadejte adresář, kde se budou hledat soubory
echo "Zadejte adresář, kde budou soubory hledány:"
read directory

# Pokud adresář neexistuje, požádáme o nový
while [ ! -d "$directory" ]; do
    echo "Adresář $directory neexistuje. Zadejte platný adresář:"
    read directory
done

# Hledání požadovaných souborů v zadaném adresáři
ask_for_file_in_directory "$directory" "common.py"
ask_for_file_in_directory "$directory" "lan_multiplayer_menu.py"
ask_for_file_in_directory "$directory" "lan_multiplayer_client.py"
ask_for_file_in_directory "$directory" "lan_multiplayer_server.py"
ask_for_file_in_directory "$directory" "local_multiplayer.py"
ask_for_file_in_directory "$directory" "singleplayer.py"

# Hledání ikony pro AppImage
echo "Zadejte cestu k ikoně (např. czess-icon.png):"
read iconpath
while [ ! -f "$iconpath" ]; do
    echo "Ikona nebyla nalezena. Zadejte platnou cestu k ikoně:"
    read iconpath
done

# Volba EXE nebo AppImage
echo "Chcete vytvořit EXE (Windows) nebo AppImage (Linux)? (zadejte 'exe' nebo 'appimage')"
read choice

if [ "$choice" == "exe" ]; then
    echo "Vytvářím EXE pro Windows..."

    # 1. Vytvoření EXE souboru pro Windows pomocí PyInstaller
    pyinstaller main.py -y -F -w --add-data "$common_py:. --add-data $lan_multiplayer_menu_py:. --add-data $lan_multiplayer_client_py:. --add-data $lan_multiplayer_server_py:. --add-data $local_multiplayer_py:. --add-data $singleplayer_py:. --clean --optimize 2

    echo "EXE soubor byl vytvořen."

elif [ "$choice" == "appimage" ]; then
    echo "Vytvářím AppImage pro Linux..."

    # 1. Vytvoření binárního souboru pomocí PyInstaller
    pyinstaller main.py -y -F -w --add-data "$common_py:. --add-data $lan_multiplayer_menu_py:. --add-data $lan_multiplayer_client_py:. --add-data $lan_multiplayer_server_py:. --add-data $local_multiplayer_py:. --add-data $singleplayer_py:. --clean --optimize 2

    # 2. Vytvoření struktury AppDir
    mkdir -p dist/AppDir/usr/bin
    mkdir -p dist/AppDir/usr/share/applications
    mkdir -p dist/AppDir/usr/share/icons/hicolor/256x256/apps

    # 3. Přesun binárního souboru do AppDir
    cp dist/main dist/AppDir/usr/bin/

    # 4. Vytvoření .desktop souboru
    cat <<EOF > dist/AppDir/usr/share/applications/czess.desktop
[Desktop Entry]
Version=1.0
Name=Czess
Comment=Chess on Python
Exec=main
Icon=czess-icon
Terminal=false
Type=Application
Categories=Game;
EOF

    # 5. Přidání ikony do AppDir
    cp "$iconpath" dist/AppDir/usr/share/icons/hicolor/256x256/apps/czess-icon.png

    # 6. Vytvoření AppImage pomocí linuxdeploy
    ./linuxdeploy-x86_64.AppImage --appdir dist/AppDir --output appimage

    echo "AppImage soubor byl vytvořen."

else
    echo "Neplatná volba. Zkuste to znovu a zadejte 'exe' nebo 'appimage'."
fi

