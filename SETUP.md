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

RPi 2 additionally requires a minimal X server:

```bash
sudo apt install xserver-xorg xinit x11-xserver-utils
```

---

### Display Driver

mclocks needs to know how to reach the display. This depends on your hardware:

| Model | Driver | Notes |
|-------|--------|-------|
| RPi 2 | `x11` | No EGL/KMS support; X server started internally by launcher |
| RPi 3 / 4 / 5 | `kmsdrm` | Direct console rendering, no X needed |

The `mclocks` launcher detects your hardware and handles everything automatically.

---

### CLI Mode + Auto-login (Optional)

For an always-on display, configure the Pi to boot to CLI and log in automatically.

**Set CLI boot mode:**

```bash
sudo systemctl set-default multi-user.target
```

**Enable auto-login on tty1:**

```bash
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $USER --noclear %I \$TERM
EOF
sudo systemctl daemon-reload
```

---

### Auto-start on Boot (Optional)

Once CLI mode and auto-login are configured, add the following to `~/.bash_profile` to launch mclocks automatically on login:

```bash
cat >> ~/.bash_profile << 'EOF'

# Auto-start mclocks on tty1
if [ "$(tty)" = "/dev/tty1" ]; then
    mclocks 2
fi
EOF
```

> To use the 2×2 four-clock layout instead, change `mclocks 2` to `mclocks 4`.

---

## Timezones

mclocks reads timezone configuration from `mclocks.conf`, located alongside `mclocks.py` in `/usr/local/lib/mclocks/`. Edit it to set your preferred cities and timezones:

```ini
[locations]
location1 = LOCAL, local
location2 = SAN FRANCISCO, America/Los_Angeles
location3 = SINGAPORE, Asia/Singapore
location4 = NEW YORK, America/New_York
```

Use `local` as the timezone value to auto-detect from the system. Timezone strings follow the IANA format — see the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for a full list.

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

## Themes

mclocks ships with two built-in themes, selectable at runtime or via config:

| Theme | Style |
|-------|-------|
| `vibrant` | Full circadian spectrum — cool blues and whites by day, warm reds by night |
| `warm` | Amber and red tones throughout — easier on the eyes in dark environments |

Set a default in `mclocks.conf`:

```ini
[settings]
default_theme = warm
```

Or override at runtime:

```bash
mclocks 2 warm
mclocks 4 vibrant
```

---

## Fonts

mclocks uses **JetBrains Mono** and **Inter**, both under the SIL Open Font License. The fonts are bundled in the repository under `fonts/` and installed automatically by `install.sh` to `/usr/local/lib/mclocks/fonts/`.

If running manually without installing, ensure the `fonts/` folder is in the same directory as `mclocks.py`. If fonts are missing, the app will fall back to a system sans-serif font.