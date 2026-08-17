#!/bin/bash
# Dezinstalare GDC Production Manager (Mac)
# Ruleaza direct (dublu-click) - nu are nevoie de Terminal deschis manual.

set -e
cd "$(dirname "$0")"

DATA_DIR="$HOME/Library/Application Support/GDCProductionManager"

# Cale normala + calea gresita in care ajungeau instalarile facute cu
# pachete .pkg mai vechi (pana la v1.1.5 inclusiv, bug de packaging
# reparat in v1.1.6) - verificam pe amandoua, ca sa curatam orice a
# ramas, indiferent cu ce versiune s-a instalat.
APP_PATHS=(
    "/Applications/GDCProductionManager.app"
    "/Applications/Applications/GDCProductionManager.app"
)

echo "=================================================="
echo " Dezinstalare GDC Production Manager"
echo "=================================================="
echo

FOUND_ANY=0
for p in "${APP_PATHS[@]}"; do
    if [ -d "$p" ]; then
        FOUND_ANY=1
    fi
done
if [ "$FOUND_ANY" -eq 0 ]; then
    echo "Nu am gasit aplicatia instalata (nici la calea normala, nici la cea veche, gresita)."
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

for APP_PATH in "${APP_PATHS[@]}"; do
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
done

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
