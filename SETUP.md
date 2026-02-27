# mclocks — Setup Guide

This guide covers platform-specific setup for running mclocks. Choose your platform below.

---

## Raspberry Pi

### Recommended OS by Model

| Model | OS | Architecture |
|-------|----|-------------|
| RPi 2 | Raspberry Pi OS Bookworm Lite (32-bit) | armhf |
| RPi 3 / 4 / 5 | Raspberry Pi OS Bookworm Lite (64-bit) | arm64 |

> **Note:** Trixie (RPi OS 13) is not recommended — SDL2 2.32+ drops console display support required by mclocks.

---

### Dependencies

```bash
sudo apt update
sudo apt install python3-pygame python3-tz
```

---

### Display Driver

mclocks needs to know how to reach the display. This depends on your hardware:

| Model | Driver | Notes |
|-------|--------|-------|
| RPi 2 | `x11` | No EGL/KMS support; requires a minimal X server |
| RPi 3 / 4 / 5 | `kmsdrm` | Direct console rendering, no X needed |

The `mclocks` launcher script detects your hardware and sets the correct driver automatically.

---

### RPi 2 — Additional Setup (x11)

RPi 2 cannot use KMS/DRM due to hardware limitations. A minimal X server is required.

**Install X:**

```bash
sudo apt install xserver-xorg xinit x11-xserver-utils
```

**Configure `~/.xinitrc`:**

```bash
cat > ~/.xinitrc << 'EOF'
#!/bin/bash
# Disable screen blanking
xset s off
xset s noblank
xset -dpms

# Launch mclocks
mclocks 2
EOF
chmod +x ~/.xinitrc
```

**Run manually:**

```bash
startx
```

---

### Auto-start on Boot (Optional)

To launch mclocks automatically when the Pi boots and logs in on tty1, add the following to `~/.bash_profile`:

**RPi 2 (via startx):**

```bash
cat >> ~/.bash_profile << 'EOF'

# Auto-start mclocks on tty1
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    startx
fi
EOF
```

**RPi 3 / 4 / 5 (direct):**

```bash
cat >> ~/.bash_profile << 'EOF'

# Auto-start mclocks on tty1
if [ "$(tty)" = "/dev/tty1" ]; then
    mclocks 2
fi
EOF
```

> To use the 2×2 four-clock layout instead, change `mclocks 2` to `mclocks 4` in the line you added to `~/.bash_profile`.

---

## macOS (Development / Testing)

macOS is supported for local development using a Python virtual environment. pygame uses its native display driver automatically — no extra configuration needed.

### Requirements

- Python 3.9 or later
- Homebrew (recommended)

### Setup

```bash
# Clone the repo
git clone https://github.com/yusungchang/mclocks.git
cd mclocks

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install pygame pytz

# Run
python3 mclocks.py 2
```

To deactivate the virtual environment:

```bash
deactivate
```

> The `mclocks` shell wrapper is intended for Raspberry Pi. On macOS, run `python3 mclocks.py` directly or create your own alias.

---

## Fonts

mclocks uses **JetBrains Mono** and **Inter**, both under the SIL Open Font License. The fonts are bundled in the repository under `fonts/` and installed automatically by `install.sh` to `/usr/local/lib/mclocks/fonts/`.

If running manually without installing, ensure the `fonts/` folder is in the same directory as `mclocks.py`. If fonts are missing, the app will fall back to a system sans-serif font.