#!/bin/bash
# =================================================================
#  raspi3-fastboot-disable.sh
#  Revert Fastboot tweaks and restore original system state.
#
#  !!! WARNING !!! WARNING !!! WARNING !!! WARNING
#  This script is designed ONLY for Raspberry Pi 3 running
#  Debian 12 (Bookworm).
#
#  This script modifies Raspberry Pi boot configuration.
#  Proceed with caution. Incorrect use may alter the boot
#  sequence and could render the system unbootable or cause
#  hardware misconfiguration.
#
#  Review and understand the script before running it.
#
#  Installation: /usr/local/sbin
#  Copyright (c) 2026 Yu-Sung Chang | MIT License
# =================================================================

# --- USER CONFIGURATION ---
TARGET_USER="yusung"       # Should match the user in the enable script
# --------------------------

echo "--- 1. Preflight Check ---"
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Try: sudo $0"
   exit 1
fi

# Configuration Paths
STATE_FILE="/var/lib/raspi3-fastboot/enabled"
BACKUP_LATEST="/var/lib/raspi3-fastboot/backups/latest"

# --- 1. Check State ---
if [[ ! -f "$STATE_FILE" ]]; then
    echo "ERROR: Fastboot is not currently enabled (State file missing)."
    exit 1
fi

if [[ ! -L "$BACKUP_LATEST" ]]; then
    echo "ERROR: Backup directory link not found at $BACKUP_LATEST"
    exit 1
fi

echo "--- 2. Restoring Original Configuration Files ---"
restore_file() {
    local src="$BACKUP_LATEST/$(basename "$1")"
    if [[ -f "$src" ]]; then
        cp "$src" "$1"
        echo " [OK] Restored: $1"
    else
        echo " [SKIP] $1 (Original backup not found)"
    fi
}

restore_file /boot/firmware/config.txt
restore_file /boot/firmware/cmdline.txt
restore_file /etc/systemd/system/getty@tty1.service.d/autologin.conf
restore_file /etc/issue
restore_file /etc/issue.net
restore_file /etc/motd

echo "--- 3. Unmasking Background Services ---"
# Should match with the enable script
systemctl unmask ModemManager.service
systemctl unmask bluetooth.service
systemctl unmask hciuart.service
#systemctl unmask sound.target
#systemctl unmask alsa-restore.service
#systemctl unmask alsa-state.service

echo "--- 4. Re-enabling System Services ---"
systemctl enable NetworkManager-wait-online.service
systemctl enable dphys-swapfile.service
systemctl enable keyboard-setup.service
systemctl enable triggerhappy.service
# Should match with the enable script
#systemctl enable avahi-daemon.service

echo "--- 5. Cleaning Up ---"
# Remove the hushlogin for the specific user
if [[ -f "/home/$TARGET_USER/.hushlogin" ]]; then
    rm "/home/$TARGET_USER/.hushlogin"
    echo " [OK] Removed .hushlogin for $TARGET_USER"
fi

# Remove the lock file to allow future enablement
rm -f "$STATE_FILE"
echo " [OK] System state unlocked"

# Reload systemd to recognize the restored getty configuration
systemctl daemon-reload

echo "---------------------------------------------------"
echo "RESTORE COMPLETE!"
echo "System has been returned to standard configuration."
echo "Reboot recommended: sudo reboot now"
echo "---------------------------------------------------"
