#!/bin/bash
# File: /usr/local/bin/launcher.sh
# Make sure to chmod +x this file

# ----------------------------
# CONFIGURATION
# ----------------------------
# List of apps (full path)
APPS=(
    "/usr/local/bin/youtube"
    "/usr/local/bin/mclocks"
)

# Corresponding descriptions
DESCRIPTIONS=(
    "YouTube News Channel Player"
    "Multi-timezone World Clock"
)

# ----------------------------
# INTERNAL VARIABLES
# ----------------------------
selected=0   # currently highlighted menu item

# ----------------------------
# FUNCTIONS
# ----------------------------
draw_menu() {
    clear
    echo "========================================================="
    echo "                  APPLICATION LAUNCHER"
    echo ""
    echo "      Use ↑ ↓ arrows | Enter to select | Q to quit"
    echo "========================================================="
    echo ""
    for i in "${!APPS[@]}"; do
        line="$(basename "${APPS[$i]}") - ${DESCRIPTIONS[$i]}"
        if [[ $i -eq $selected ]]; then
            # Highlight the selected line
            echo -e "> \e[7m$line\e[0m"
        else
            echo "  $line"
        fi
    done
}

# ----------------------------
# MAIN LOOP
# ----------------------------
# Hide cursor
tput civis

# Ensure cursor is restored on exit
trap "tput cnorm; clear; exit" SIGINT SIGTERM EXIT

while true; do
    draw_menu

    # Read single key press
    read -rsn1 key
    if [[ $key == $'\x1b' ]]; then
        # Arrow key sequence
        read -rsn2 key
        if [[ $key == "[A" ]]; then
            ((selected--))
            [[ $selected -lt 0 ]] && selected=$((${#APPS[@]} - 1))
        elif [[ $key == "[B" ]]; then
            ((selected++))
            [[ $selected -ge ${#APPS[@]} ]] && selected=0
        fi
    elif [[ $key == "" ]]; then
        # Enter pressed → run the selected app
        tput cnorm
        clear
        "${APPS[$selected]}"
        echo "App closed. Returning to menu..."
        tput civis
        sleep 0.5
    elif [[ $key == "q" ]]; then
        # Quit
        clear
        exit 0
    fi
done

# Restore cursor before exiting
tput cnorm
clear
