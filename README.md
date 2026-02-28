# mclocks — for Raspberry Pi

> A pygame-based multi-timezone world clock for always-on Raspberry Pi displays — 2-pane or 2×2 layout, LED dot-matrix digits, and time-of-day circadian colors.

---

## Features

- 🕐 LED dot-matrix clock rendered with pygame — no desktop required
- 🌍 2-pane (top/bottom) or 2×2 layout
- 🎨 Circadian color — each clock shifts color by its own local time of day
- 🎭 Themes — `vibrant` (default) and `warm`, switchable at runtime
- 📅 Day-of-week tracker and date display per pane
- 🌐 Local timezone auto-detection for the home pane
- ⚙️ Config file for timezones and default theme
- 🖥️ Designed for always-on Raspberry Pi displays (800×480)
- 🔠 JetBrains Mono font — bundled, no system font needed

---

## Requirements

- Raspberry Pi OS Bookworm Lite
- Python 3.11 or later — `sudo apt install python3`
- pygame — `sudo apt install python3-pygame`
- pytz — `sudo apt install python3-tz`
- RPi 2 only: X11 — `sudo apt install xserver-xorg xinit x11-xserver-utils`

See [SETUP.md](SETUP.md) for recommended OS by model, display driver details, and macOS development setup.

---

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/yusungchang/mclocks/main/install.sh | sudo bash
```

You can inspect [`install.sh`](install.sh) before running.

Installs:
- `/usr/local/bin/mclocks` — launcher
- `/usr/local/lib/mclocks/mclocks.py` — main script
- `/usr/local/lib/mclocks/mclocks.conf` — configuration
- `/usr/local/lib/mclocks/fonts/` — JetBrains Mono, Inter

---

## Usage

```
mclocks [MODE] [THEME]
```

| Argument | Values | Default |
|----------|--------|---------|
| `MODE` | `2` (top/bottom), `4` (2×2 grid) | `4` |
| `THEME` | `vibrant`, `warm` | `vibrant` |

```bash
mclocks          # 2×2 layout, vibrant theme
mclocks 2        # top/bottom layout, vibrant theme
mclocks 4 warm   # 2×2 layout, warm theme
mclocks 2 warm   # top/bottom layout, warm theme
```

---

## Configuration

Edit `/usr/local/lib/mclocks/mclocks.conf` to set your timezones and default theme:

```ini
[settings]
default_theme = vibrant

[locations]
location1 = LOCAL, local
location2 = SAN FRANCISCO, America/Los_Angeles
location3 = SINGAPORE, Asia/Singapore
location4 = NEW YORK, America/New_York
```

Use `local` as the timezone value to auto-detect from the system. See the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for timezone strings.

Display order:

| Mode | Position |
|------|----------|
| `mclocks 2` | 1=top, 2=bottom |
| `mclocks 4` | 1=top-left, 2=bottom-left, 3=top-right, 4=bottom-right |

---

## Themes

| Theme | Description |
|-------|-------------|
| `vibrant` | Full circadian spectrum — dark red night through cyan midday to white peak |
| `warm` | Amber and red tones throughout the day |

---

## Circadian Colors (vibrant)

Each pane colors itself by its own local time of day.

| Hours | Color | Period |
|-------|-------|--------|
| 00–04 | Dark red | Night |
| 04–06 | Orange | Dawn |
| 06–08 | Yellow | Sunrise |
| 08–11 | Light blue | Morning |
| 11–13 | Pale cyan | Midday |
| 13–15 | White | Peak |
| 15–17 | Pale cyan | Afternoon |
| 17–19 | Blue | Evening |
| 19–21 | Orange | Sunset |
| 21–22 | Dark orange | Dusk |
| 22–24 | Dark red | Night |

---

## Auto-start on Boot

See [SETUP.md](SETUP.md) for instructions on auto-launching mclocks when the Pi boots.

---

## License

MIT © 2026 Yu-Sung Chang — see [LICENSE](LICENSE) for terms.