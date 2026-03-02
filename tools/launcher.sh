#!/bin/bash
# ==============================================================================
#  App Launcer
#  Copyright (c) 2026 Yu-Sung Chang
# ==============================================================================

while true; do

CHOICE=$(whiptail \
    --title "Application Launcher" \
    --menu "Select application" \
    15 50 5 \
    youtube "YouTube New Channel Player" \
    mclocks "Multi-timezone World Clock" \
    quit "Exit launcher" \
    3>&1 1>&2 2>&3)

clear

case "$CHOICE" in
    youtube)
        /usr/local/bin/youtube
        ;;
    mclocks)
        /usr/local/bin/mclocks
        ;;
    quit)
        exit 0
        ;;
esac

done
