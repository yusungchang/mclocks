#!/bin/bash

while true; do

CHOICE=$(whiptail \
    --title "Application Launcher" \
    --menu "Select application" \
    15 50 6 \
    yt-news "    YouTube New Channel Player" \
    mclocks "    Multi-timezone World Clock" \
    Reboot  "    Reboot the System" \
    Quit    "    Exit Launcher" \
    3>&1 1>&2 2>&3)

clear

case "$CHOICE" in
    yt-news)
        /usr/local/bin/yt-news
        ;;
    mclocks)
        /usr/local/bin/mclocks
        ;;
    Reboot)
        sudo reboot now
        ;;
    Quit)
        exit 0
        ;;
esac

done
