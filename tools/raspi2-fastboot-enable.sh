#!/bin/bash
# =================================================================
# raspi2-fastboot-enable.sh
# Tweak boot sequences for silent and ultra-fast booting.
#
# !!! WARNING !!! WARNING !!! WARNING !!! WARNING
# This script is designed ONLY for Raspberry Pi 2 running
# Debian 12 (Bookworm). Using this on other models or
# distributions may destroy the booting sequence or result 
# in hardware misconfiguration.
#
# Proceed with caution.
#
# Installation: /usr/local/sbin
# Copyright (c) 2026 Yu-Sung Chang | MIT License
# =================================================================

# --- USER CONFIGURATION: MODIFY THESE ---
TARGET_USER="yusung"       # The user for autologin
WIDTH=800                  # Screen Width (px)
HEIGHT=480                 # Screen Height (px)
REFRESH=60                 # Refresh Rate (Hz)
# ----------------------------------------

echo "--- 1. Preflight Check ---"
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Try: sudo $0"
   exit 1
fi

# Confirm device model
MODEL=$(tr -d '\0' </proc/device-tree/model)
if [[ "$MODEL" != *"Raspberry Pi 2"* ]]; then
    echo "ERROR: This script is ONLY for Raspberry Pi 2"
    exit 1
fi

# Configuration Paths
STATE_FILE="/var/lib/raspi2-fastboot/enabled"
BACKUP_ROOT="/var/lib/raspi2-fastboot/backups"
TS=$(date +%Y%m%d_%H%M)
BACKUP_DIR="$BACKUP_ROOT/$TS"
LATEST_LINK="$BACKUP_ROOT/latest"

# --- 1. State Locking ---
if [[ -f "$STATE_FILE" ]]; then
    echo "ERROR: Fastboot is already enabled."
    echo "Please run 'raspi2-fastboot-disable.sh' before running this again."
    exit 1
fi

mkdir -p "$BACKUP_DIR"

echo "--- 2. Backing up Original Configs to $BACKUP_DIR ---"
smart_bak() {
    [ -f "$1" ] && cp "$1" "$BACKUP_DIR/$(basename "$1")"
}

smart_bak /boot/firmware/config.txt
smart_bak /boot/firmware/cmdline.txt
smart_bak /etc/systemd/system/getty@tty1.service.d/autologin.conf
smart_bak /etc/issue
smart_bak /etc/issue.net
smart_bak /etc/motd

# Update the 'latest' symlink for the disable script
rm -f "$LATEST_LINK"
ln -s "$BACKUP_DIR" "$LATEST_LINK"

echo "--- 3. Hardware Level Silence (config.txt) ---"
# Remove existing instances of these settings to prevent duplicates
# AUDIO DISABLED
sed -i '/disable_splash=/d; /boot_delay=/d; /dtparam=audio=/d; /dtparam=sd_poll_once=/d' /boot/firmware/config.txt

cat <<EOF >> /boot/firmware/config.txt
# Added by raspi2-fastboot-enable.sh
disable_splash=1
boot_delay=0
# AUDIO DISABLED
dtparam=audio=off
dtparam=sd_poll_once=on
# Display specific timings (MAY REQUIRE MODIFICATION))
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=$WIDTH $HEIGHT $REFRESH 6 0 0 0
hdmi_drive=1 # AUDIO DISABLED
EOF

echo "--- 4. Kernel & Terminal Silence (cmdline.txt) ---"
# Force frame buffer to match defined resolution (MAY REQUIRE MODIFICATION))
sed -i "s/console=tty1/console=tty1 quiet loglevel=3 vt.global_cursor_default=0 logo.nologo fastboot video=HDMI-A-1:${WIDTH}x${HEIGHT}@${REFRESH}D/g" /boot/firmware/cmdline.txt

# Emptying the banners
truncate -s 0 /etc/issue /etc/issue.net /etc/motd

echo "--- 5. Pushing Silent Autologin Overrides ---"
mkdir -p /etc/systemd/system/getty@tty1.service.d/
# agetty flags are very sensitive. MAY REQUIRE MODIFICATION
cat <<EOF > /etc/systemd/system/getty@tty1.service.d/autologin.conf
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $TARGET_USER --skip-login --noclear --noissue %I \$TERM
Type=simple
EOF

echo "--- 6. Disabling Performance-Heavy Services ---"
systemctl disable NetworkManager-wait-online.service
systemctl disable dphys-swapfile.service
systemctl disable keyboard-setup.service
systemctl disable triggerhappy.service
# mDNS ENABLED
#systemctl disable avahi-daemon.service

echo "--- 7. Masking Multimedia/Background Services ---"
# If you need sound, MODIFY HERE ACCORDINGLY
systemctl mask ModemManager.service
systemctl mask sound.target
# AUDIO DISABLED
systemctl mask alsa-restore.service
systemctl mask alsa-state.service

echo "--- 8. User Level Silence (.hushlogin) ---"
touch /home/$TARGET_USER/.hushlogin
touch "$STATE_FILE"
systemctl daemon-reload

echo "---------------------------------------------------"
echo "FASTBOOT ENABLED SUCCESSFULLY!"
echo "Backup location: $BACKUP_DIR"
echo "Target User: $TARGET_USER"
echo "Resolution:  ${WIDTH}x${HEIGHT} @ ${REFRESH}Hz"
echo "Please reboot to see changes."
echo "---------------------------------------------------"
