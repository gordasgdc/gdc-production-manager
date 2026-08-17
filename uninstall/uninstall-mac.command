#!/bin/bash
# Dezinstalare GDC Production Manager (Mac)
# Ruleaza direct (dublu-click) - nu are nevoie de Terminal deschis manual.

set -e
cd "$(dirname "$0")"

APP_PATH="/Applications/GDCProductionManager.app"
DATA_DIR="$HOME/Library/Application Support/GDCProductionManager"

echo "=================================================="
echo " Dezinstalare GDC Production Manager"
echo "=================================================="
echo

if [ ! -d "$APP_PATH" ]; then
    echo "Nu am gasit $APP_PATH - aplicatia nu pare instalata (sau e in alt loc)."
fi

# Opreste aplicatia daca ruleaza, ca sa nu ramana fisiere blocate.
if pgrep -x "GDCProductionManager" > /dev/null 2>&1; then
    echo "Opresc aplicatia care ruleaza..."
    pkill -x "GDCProductionManager" 2>/dev/null || true
    sleep 1
fi

read -p "Stergi si datele salvate (conturi, proiecte, licenta)? [y/N] " -n 1 -r DELETE_DATA
echo
echo

if [ -d "$APP_PATH" ]; then
    echo "Sterg $APP_PATH ..."
    if rm -rf "$APP_PATH" 2>/dev/null; then
        echo "  OK."
    else
        echo "  Am nevoie de parola de administrator (instalata prin .pkg, detinuta de root):"
        sudo rm -rf "$APP_PATH"
        echo "  OK."
    fi
fi

if [[ "$DELETE_DATA" =~ ^[Yy]$ ]]; then
    if [ -d "$DATA_DIR" ]; then
        echo "Sterg datele din $DATA_DIR ..."
        rm -rf "$DATA_DIR"
        echo "  OK."
    fi
else
    echo "Pastrez datele din $DATA_DIR (le poti sterge manual oricand)."
fi

echo
echo "Dezinstalare terminata."
read -p "Apasa Enter ca sa inchizi fereastra..." _
