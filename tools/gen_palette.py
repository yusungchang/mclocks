#!/usr/bin/env python3
# Generate assets/palette.png — circadian color palette for all themes.
# Run from the repo root: python3 tools/gen_palette.py

from PIL import Image, ImageDraw, ImageFont
import os

THEMES = {
    "vibrant": {
        "background": (5, 5, 5),
        "circadian": [
            (0,  (110, 20,  20)),
            (4,  (230, 90,  40)),
            (6,  (255, 180, 50)),
            (8,  (140, 210, 255)),
            (11, (180, 240, 255)),
            (13, (255, 255, 255)),
            (15, (180, 240, 255)),
            (17, (120, 180, 240)),
            (19, (255, 130, 60)),
            (21, (180, 50,  40)),
            (22, (110, 20,  20)),
        ]
    },
    "warm": {
        "background": (8, 4, 0),
        "circadian": [
            (0,  (80,  20,  5)),
            (4,  (160, 60,  10)),
            (6,  (220, 120, 30)),
            (8,  (255, 180, 80)),
            (11, (255, 210, 120)),
            (13, (255, 230, 160)),
            (15, (255, 200, 100)),
            (17, (240, 150, 50)),
            (19, (210, 90,  20)),
            (21, (140, 40,  10)),
            (22, (80,  20,  5)),
        ]
    },
    "fjord": {
        "background": (3, 4, 8),
        "circadian": [
            (0,  (145, 65,  15)),
            (4,  (235, 125, 20)),
            (6,  (250, 200, 80)),
            (8,  (215, 200, 170)),
            (11, (180, 210, 245)),
            (13, (240, 245, 255)),
            (15, (180, 210, 245)),
            (17, (215, 200, 170)),
            (19, (250, 200, 80)),
            (21, (235, 125, 20)),
            (22, (145, 65,  15)),
        ]
    },
    "cold": {
        "background": (6, 10, 22),
        "circadian": [
            (0,  (34, 48, 110)),   # Night
            (4,  (56, 82, 165)),   # Dawn
            (6,  (82, 128, 225)),  # Sunrise
            (8,  (118, 168, 250)), # Morning
            (11, (165, 210, 255)), # Midday
            (13, (195, 230, 255)), # Peak
            (15, (155, 205, 255)), # Afternoon
            (17, (120, 175, 240)), # Evening
            (19, (90, 140, 215)),  # Sunset
            (21, (62, 95, 175)),   # Dusk
            (22, (34, 48, 110)),   # Night
        ]
    },
}

def get_color(hour, stops):
    for i in range(len(stops) - 1):
        if stops[i][0] <= hour < stops[i+1][0]:
            return stops[i][1]
    return stops[-1][1]

# Layout constants
HOURS = 24
CELL_W = 32
CELL_H = 80
LABEL_W = 100
TICK_H = 24
PAD = 20
THEME_GAP = 12

FONT_PATH = os.path.join(os.path.dirname(__file__), "../fonts", "Inter-Bold.ttf")

total_w = PAD + LABEL_W + HOURS * CELL_W + PAD
n_themes = len(THEMES)
total_h = PAD + n_themes * CELL_H + (n_themes - 1) * THEME_GAP + TICK_H + PAD

img = Image.new("RGB", (total_w, total_h), (12, 12, 12))
draw = ImageDraw.Draw(img)

try:
    font_label = ImageFont.truetype(FONT_PATH, 18)
    font_tick  = ImageFont.truetype(FONT_PATH, 13)
except Exception:
    font_label = ImageFont.load_default()
    font_tick  = font_label

y0 = PAD
for idx, (name, theme) in enumerate(THEMES.items()):
    y = y0 + idx * (CELL_H + THEME_GAP)

    # Theme label (vertically centered in the strip)
    label_x = PAD
    label_y = y + CELL_H // 2
    draw.text((label_x, label_y), name, font=font_label, fill=(200, 200, 200), anchor="lm")

    # Color cells
    for h in range(HOURS):
        color = get_color(h, theme["circadian"])
        x = PAD + LABEL_W + h * CELL_W
        draw.rectangle([x, y, x + CELL_W - 1, y + CELL_H - 1], fill=color)

# Hour ticks (0, 6, 12, 18, 24) below the strips
tick_y = y0 + n_themes * (CELL_H + THEME_GAP) - THEME_GAP + 6
for h in [0, 6, 12, 18, 24]:
    x = PAD + LABEL_W + h * CELL_W
    label = f"{h:02d}"
    draw.text((x, tick_y), label, font=font_tick, fill=(140, 140, 140), anchor="lt")

out_path = os.path.join(os.path.dirname(__file__), "../assets", "palette.png")
img.save(out_path)
print(f"Saved {out_path}")
