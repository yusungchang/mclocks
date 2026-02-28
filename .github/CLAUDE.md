# CLAUDE.md — mclocks project context

This file provides context for AI assistants (Claude Code, etc.) working on this project.

---

## What is mclocks

A pygame-based multi-timezone world clock for always-on Raspberry Pi displays. Renders LED dot-matrix clocks in a 2-pane or 2×2 grid layout, with circadian time-of-day colors and themeing support. Designed for 800×480 HDMI displays.

---

## Repository Structure

```
mclocks/
├── mclocks.py            # Main Python app
├── mclocks               # Shell wrapper / launcher (no extension)
├── mclocks.conf          # User configuration (timezones, default theme)
├── install.sh            # Install script (Raspberry Pi)
├── .github/
│   ├── CLAUDE.md             # This file (AI assistant context)
│   └── workflows/
├── README.md
├── SETUP.md              # Platform-specific setup guide
├── LICENSE
├── .gitignore
├── .github/
│   └── workflows/
│       └── release.yml   # Tag-based GitHub release workflow
└── fonts/
    ├── JetBrainsMono-Regular.ttf
    ├── JetBrainsMono-Bold.ttf
    ├── JetBrainsMono-ExtraBold.ttf
    ├── Inter-Regular.ttf
    ├── Inter-Bold.ttf
    └── Inter-ExtraBold.ttf
```

---

## Installed File Locations (Raspberry Pi)

| File | Installed Path |
|------|---------------|
| Launcher | `/usr/local/bin/mclocks` |
| Python script | `/usr/local/lib/mclocks/mclocks.py` |
| Config | `/usr/local/lib/mclocks/mclocks.conf` |
| Fonts | `/usr/local/lib/mclocks/fonts/` |

`mclocks.py` resolves all paths relative to its own location (`SCRIPT_DIR`), so it works both installed and run locally from the repo.

---

## Key Design Decisions

### Display Driver — RPi 2 vs RPi 3+

This was a hard-won discovery through extensive debugging:

- **RPi 3/4/5 (Bookworm)**: SDL2 `kmsdrm` works directly on the console — no X server needed
- **RPi 2 (Bookworm)**: SDL2 2.26+ dropped `fbcon` and RPi 2 has no EGL/hardware acceleration for `kmsdrm`. The only working path is `x11` via a minimal X server (`startx`)
- **Trixie (RPi OS 13)**: Not supported — SDL2 2.32+ breaks console rendering entirely on RPi 2

The `mclocks` wrapper handles this transparently — it detects the hardware via `/proc/device-tree/model`, starts X internally for RPi 2, and sets `SDL_VIDEODRIVER` appropriately. Users always just run `mclocks 2` or `mclocks 4` regardless of hardware.

### RPi 2 X11 Approach

The wrapper creates a temporary `xinitrc`, calls `startx` internally, disables screen blanking via `xset`, and launches `mclocks.py`. No manual `.xinitrc` setup required from the user.

### 2×2 Layout — Column-Major Order

Locations are displayed in column-major order for visual consistency between `mclocks 2` and `mclocks 4`:

```
mclocks 2:    mclocks 4:
┌─────────┐   ┌────┬────┐
│  loc 1  │   │ 1  │ 3  │
├─────────┤   ├────┼────┤
│  loc 2  │   │ 2  │ 4  │
└─────────┘   └────┴────┘
```

Location 1 is always top-left, location 2 is always below it — consistent across both modes.

### Config File

`mclocks.conf` (INI format) lives alongside `mclocks.py` in the lib directory. It is:
- **Not overwritten on reinstall** — `install.sh` skips download if it already exists, preserving user edits
- **Optional** — `mclocks.py` has hardcoded defaults as fallback if config is missing or corrupt
- **Downloaded as a release asset** on first install

### Local Timezone

Location1 defaults to `local` timezone — auto-detected from `/etc/timezone` on Linux. The city name is derived from the timezone string (e.g. `Asia/Seoul` → `SEOUL`).

### Theme System

Themes are defined as dicts in `mclocks.py` under `THEMES`. Each theme controls:
- `circadian`: list of `(hour, (R, G, B))` tuples — flexible number of stops
- `background`: screen fill color
- `dim_dot`: inactive LED dot color
- `dim_text`: inactive day-of-week text color

Current themes: `vibrant` (default), `warm`.

Theme selection priority: CLI arg > `mclocks.conf` `default_theme` > hardcoded default (`vibrant`).

### Version Stamping

`@@VERSION@@` placeholder in both `mclocks` and `mclocks.py` is replaced by the release workflow (`sed`) when a tag is pushed. Never edit the version manually.

---

## Usage

```bash
mclocks [2|4] [theme]

mclocks          # 2×2, vibrant
mclocks 2        # top/bottom, vibrant
mclocks 4 warm   # 2×2, warm theme
mclocks 2 warm   # top/bottom, warm theme
```

---

## Development (macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame pytz
python3 mclocks.py 2
```

The `mclocks` shell wrapper is for Raspberry Pi only. On macOS, run `mclocks.py` directly.

---

## Release Process

```bash
git tag v1.x.x
git push origin main
git push origin v1.x.x
```

GitHub Actions stamps the version, creates the release, and attaches all assets automatically. See `.github/workflows/release.yml`.

---

## Things to Be Careful About

- **Do not auto-install apt packages** in `install.sh` — it breaks on macOS and non-RPi Linux. Check and warn only.
- **Do not overwrite `mclocks.conf`** on reinstall — users may have customized their timezones and theme.
- **Font paths** must always go through `font_path()` — never hardcode font filenames directly.
- **`mclocks.conf` is not version-stamped** — it is copied as-is to the release assets.
- **RPi 2 X11**: do not remove the `startx` approach — `kmsdrm` and `fbcon` do not work on RPi 2 with SDL2 2.26+.
- **Column-major layout**: the 2×2 grid uses `col = i // 2`, `row = i % 2` — do not change to row-major without updating docs.