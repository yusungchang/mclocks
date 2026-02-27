# mclocks — for Raspberry Pi

> A pygame-based multi-timezone world clock for always-on Raspberry Pi displays — 2-pane or 2×2 layout, LED dot-matrix digits, and time-of-day circadian colors.

---

## Features

- 🕐 LED dot-matrix clock rendered with pygame — no desktop required
- 🌍 2-pane (top/bottom) or 2×2 layout
- 🎨 Circadian color — each clock shifts color by its own local time of day
- 📅 Day-of-week tracker and date display per pane
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
- `/usr/local/lib/mclocks/fonts/` — JetBrains Mono

---

## Usage

```
mclocks [MODE]
```

| Mode | Layout | Panes |
|------|--------|-------|
| `2` | Top / bottom | 2 clocks |
| `4` (default) | 2×2 grid | 4 clocks |

```bash
mclocks      # 2×2 layout (default)
mclocks 4    # 2×2 layout (explicit)
mclocks 2    # top/bottom layout
```

---

## Timezones

| Pane | City | Timezone |
|------|------|----------|
| 1 | Seoul | Asia/Seoul |
| 2 | Singapore | Asia/Singapore |
| 3 | San Francisco | America/Los_Angeles |
| 4 | New York | America/New_York |

To change cities, edit `ALL_LOCATIONS` in `mclocks.py`.

---

## Circadian Colors

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