#!/bin/bash

# ==============================================================================
#  mclocks - Install Script
#  Downloads the latest release from GitHub and installs all files.
#
#  Usage:
#    curl -fsSL https://raw.githubusercontent.com/yusungchang/mclocks/main/install.sh | bash
#
#  Installs:
#    - /usr/local/bin/mclocks          (shell wrapper / launcher)
#    - /usr/local/lib/mclocks/mclocks.py
#    - /usr/local/lib/mclocks/fonts/   (JetBrains Mono)
# ==============================================================================

set -euo pipefail

REPO="yusungchang/mclocks"
BIN_DIR="/usr/local/bin"
LIB_DIR="/usr/local/lib/mclocks"
FONT_DIR="$LIB_DIR/fonts"

BASE_URL="https://github.com/$REPO/releases/latest/download"

echo "Installing mclocks to $BIN_DIR and $LIB_DIR..."
echo ""

# --- REQUIRE SUDO ---
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run with sudo." >&2
    echo "  sudo bash install.sh" >&2
    exit 1
fi

# --- CHECK DEPENDENCIES ---
echo "Checking dependencies..."

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is not installed. Please run: sudo apt install python3" >&2
    exit 1
fi

if ! python3 -c "import pygame" &>/dev/null; then
    echo "Error: pygame not found. Please run: sudo apt install python3-pygame" >&2
    exit 1
fi

if ! python3 -c "import pytz" &>/dev/null; then
    echo "Error: pytz not found. Please run: sudo apt install python3-tz" >&2
    exit 1
fi

# RPi 2 requires X11
MODEL=$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || echo "")
if echo "$MODEL" | grep -q "Raspberry Pi 2"; then
    if ! command -v startx &>/dev/null; then
        echo "Error: X11 not found. Please run: sudo apt install xserver-xorg xinit x11-xserver-utils" >&2
        exit 1
    fi
fi

echo ""

# --- CREATE DIRECTORIES ---
mkdir -p "$LIB_DIR"
mkdir -p "$FONT_DIR"

# --- DOWNLOAD WRAPPER ---
echo "Downloading mclocks (launcher)..."
if ! curl -fsSL "$BASE_URL/mclocks" -o "$BIN_DIR/mclocks"; then
    echo "Error: Failed to download mclocks launcher" >&2
    exit 1
fi
chmod +x "$BIN_DIR/mclocks"
echo "  Installed launcher  → $BIN_DIR/mclocks"

# --- DOWNLOAD PYTHON SCRIPT ---
echo "Downloading mclocks.py..."
if ! curl -fsSL "$BASE_URL/mclocks.py" -o "$LIB_DIR/mclocks.py"; then
    echo "Error: Failed to download mclocks.py" >&2
    exit 1
fi
chmod +x "$LIB_DIR/mclocks.py"
echo "  Installed script    → $LIB_DIR/mclocks.py"

# --- DOWNLOAD FONTS ---
echo "Downloading fonts..."

FONTS=(
    "JetBrainsMono-Regular.ttf"
    "JetBrainsMono-Bold.ttf"
    "JetBrainsMono-ExtraBold.ttf"
    "Inter-Regular.ttf"
    "Inter-Bold.ttf"
    "Inter-ExtraBold.ttf"
)
for font in "${FONTS[@]}"; do
    if ! curl -fsSL "$BASE_URL/$font" -o "$FONT_DIR/$font"; then
        echo "Warning: Failed to download $font — falling back to system font" >&2
    else
        echo "  Installed font      → $FONT_DIR/$font"
    fi
done

echo ""

# --- RPi 2 POST-INSTALL NOTE ---
if echo "$MODEL" | grep -q "Raspberry Pi 2"; then
    echo "RPi 2 detected — additional setup required."
    echo ""
    echo "  Configure ~/.xinitrc to launch mclocks on startx."
    echo "  See SETUP.md for instructions:"
    echo "  https://github.com/$REPO/blob/main/SETUP.md"
    echo ""
fi

echo "Done. Run 'mclocks 2' or 'mclocks 4' to start."