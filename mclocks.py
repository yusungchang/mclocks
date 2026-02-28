#!/usr/bin/env python3
# mclocks @@VERSION@@
# A pygame-based multi-timezone world clock for Raspberry Pi displays

import pygame
import pygame.gfxdraw
import datetime
import pytz
import sys
import os
import configparser
import pathlib

# --- BASE CONFIGURATION ---
WIDTH, HEIGHT = 800, 480
BASE_SPACING = 2.5
BASE_RADIUS = 1
FPS = 10

# --- PATHS ---
# Resolve paths relative to this script's location (works both installed and local)
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FONT_DIR = os.path.join(SCRIPT_DIR, "fonts")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "mclocks.conf")

def font_path(filename):
    return os.path.join(FONT_DIR, filename)

# --- THEMES ---
THEMES = {
    "vibrant": {
        "background": (5, 5, 5),
        "dim_dot":    (25, 25, 25),
        "dim_text":   (65, 65, 65),
        "circadian": [
            (0,  (110, 20,  20)),   # Night
            (4,  (230, 90,  40)),   # Dawn
            (6,  (255, 180, 50)),   # Sunrise
            (8,  (140, 210, 255)),  # Morning
            (11, (180, 240, 255)),  # Midday
            (13, (255, 255, 255)),  # Peak
            (15, (180, 240, 255)),  # Afternoon
            (17, (120, 180, 240)),  # Evening
            (19, (255, 130, 60)),   # Sunset
            (21, (180, 50,  40)),   # Dusk
            (22, (110, 20,  20)),   # Night
        ]
    },
    "warm": {
        "background": (8, 4, 0),
        "dim_dot":    (30, 15, 5),
        "dim_text":   (70, 40, 15),
        "circadian": [
            (0,  (80,  20,  5)),    # Night
            (4,  (160, 60,  10)),   # Dawn
            (6,  (220, 120, 30)),   # Sunrise
            (8,  (255, 180, 80)),   # Morning
            (11, (255, 210, 120)),  # Midday
            (13, (255, 230, 160)),  # Peak
            (15, (255, 200, 100)),  # Afternoon
            (17, (240, 150, 50)),   # Evening
            (19, (210, 90,  20)),   # Sunset
            (21, (140, 40,  10)),   # Dusk
            (22, (80,  20,  5)),    # Night
        ]
    },
    "fjord": {
        "background": (3, 4, 8),
        "dim_dot":    (18, 20, 28),
        "dim_text":   (48, 52, 68),
        "circadian": [
            (0,  (145, 65,  15)),   # Dawn
            (4,  (235, 125, 20)),   # Sunrise
            (6,  (250, 200, 80)),   # Morning
            (8,  (215, 200, 170)),  # Late morning
            (11, (180, 210, 245)),  # Noon
            (13, (240, 245, 255)),  # Peak
            (15, (180, 210, 245)),  # Afternoon
            (17, (215, 200, 170)),  # Late afternoon
            (19, (250, 200, 80)),   # Golden hour
            (21, (235, 125, 20)),   # Sunset
            (22, (145, 65,  15)),   # Dusk
        ]
    },
}

DEFAULT_THEME = "vibrant"

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

# --- LOCAL TIMEZONE DETECTION ---
def get_local_timezone():
    try:
        tz_str = pathlib.Path('/etc/timezone').read_text().strip()
        return tz_str
    except Exception:
        pass
    try:
        tz_str = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
        return tz_str
    except Exception:
        pass
    return "UTC"

def get_local_city():
    tz = get_local_timezone()
    # Use the city part of the timezone string (e.g. "Asia/Seoul" -> "SEOUL")
    if '/' in tz:
        city = tz.split('/')[-1].replace('_', ' ').upper()
    else:
        city = tz.upper()
    return city

# --- DEFAULT LOCATIONS ---
DEFAULT_LOCATIONS = [
    ("LOCAL",         "local"),
    ("SAN FRANCISCO", "America/Los_Angeles"),
    ("SINGAPORE",     "Asia/Singapore"),
    ("NEW YORK",      "America/New_York"),
]

# --- CONFIG LOADER ---
def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)

    # Locations
    locations = []
    if config.has_section('locations'):
        for key in ['location1', 'location2', 'location3', 'location4']:
            if config.has_option('locations', key):
                value = config.get('locations', key)
                parts = [p.strip() for p in value.split(',', 1)]
                if len(parts) == 2:
                    locations.append((parts[0], parts[1]))

    if not locations:
        locations = DEFAULT_LOCATIONS

    # Resolve "local" timezone entries
    resolved = []
    for name, tz in locations:
        if tz.lower() == 'local':
            local_tz = get_local_timezone()
            local_city = get_local_city() if name.upper() == 'LOCAL' else name
            resolved.append((local_city, local_tz))
        else:
            resolved.append((name, tz))

    # Default theme from config
    default_theme = DEFAULT_THEME
    if config.has_section('settings'):
        if config.has_option('settings', 'default_theme'):
            default_theme = config.get('settings', 'default_theme').strip()

    return resolved, default_theme

DIGITS = {
    '1': ["  #  ",
          " ##  ",
          "  #  ",
          "  #  ",
          "  #  ",
          "  #  ",
          " ### "],
    '2': [" ### ",
          "#   #",
          "    #",
          "  ## ",
          " #   ",
          "#    ",
          "#####"],
    '3': ["#####",
          "    #",
          "   # ",
          "  ## ",
          "    #",
          "    #",
          "#### "],
    '4': ["   # ",
          "  ## ",
          " # # ",
          "#  # ",
          "#####",
          "   # ",
          "   # "],
    '5': ["#####",
          "#    ",
          "#### ",
          "    #",
          "    #",
          "#   #",
          " ### "],
    '6': ["  ## ",
          " #   ",
          "#    ",
          "#### ",
          "#   #",
          "#   #",
          " ### "],
    '7': ["#####",
          "    #",
          "   # ",
          "  #  ",
          " #   ",
          "#    ",
          "#    "],
    '8': [" ### ",
          "#   #",
          "#   #",
          " ### ",
          "#   #",
          "#   #",
          " ### "],
    '9': [" ### ",
          "#   #",
          "#   #",
          " ####",
          "    #",
          "   # ",
          " ##  "],
    '0': [" ### ",
          "#   #",
          "# # #",
          "# # #",
          "# # #",
          "#   #",
          " ### "],
    ':': ["     ",
          "  #  ",
          "     ",
          "     ",
          "     ",
          "  #  ",
          "     "],
    ' ': ["     ",
          "     ",
          "     ",
          "     ",
          "     ",
          "     ",
          "     "],
}

def get_circadian_color(hour, circadian_map):
    for i in range(len(circadian_map) - 1):
        if circadian_map[i][0] <= hour < circadian_map[i+1][0]:
            return circadian_map[i][1]
    return circadian_map[-1][1]

class MClockPane:
    def __init__(self, name, timezone, rect, scale, theme):
        self.name = name
        self.tz = pytz.timezone(timezone)
        self.rect = pygame.Rect(rect)
        self.scale = scale
        self.theme = theme
        self.spacing = BASE_SPACING * scale
        self.radius = int(BASE_RADIUS * scale)
        self.dim_dot = theme["dim_dot"]
        self.dim_text = theme["dim_text"]

        # Optimized font sizes
        day_sz = int(4.5 * scale)   # Slightly smaller than Location
        name_sz = int(5.5 * scale)
        info_sz = int(4 * scale)

        try:
            self.day_font = pygame.font.Font(font_path("JetBrainsMono-ExtraBold.ttf"), day_sz)
            self.name_font = pygame.font.Font(font_path("JetBrainsMono-Bold.ttf"), name_sz)
            self.info_font = pygame.font.Font(font_path("JetBrainsMono-Regular.ttf"), info_sz)
        except:
            self.day_font = pygame.font.SysFont("sans-serif", day_sz, bold=True)
            self.name_font = pygame.font.SysFont("sans-serif", name_sz, bold=True)
            self.info_font = pygame.font.SysFont("sans-serif", info_sz)

    def draw(self, surface):
        now = datetime.datetime.now(self.tz)
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d").upper()
        current_day_idx = now.weekday()
        active_color = get_circadian_color(now.hour, self.theme["circadian"])

        # Dimensions
        total_clock_w = (len(time_str) * 5 + (len(time_str)-1)) * self.spacing
        total_clock_h = 7 * self.spacing

        # 1. Calculate Positions
        # Increase gap1 to 10 * scale for more space between Days and Clock
        group_h = total_clock_h + (35 * self.scale)

        start_x = self.rect.centerx - (total_clock_w // 2)
        start_y = self.rect.centery - (group_h // 2)

        # 2. DRAW BOLD DAY-TRACK
        # Perfectly aligned with total clock width
        track_y = start_y
        track_item_w = total_clock_w / len(DAYS)
        for i, day in enumerate(DAYS):
            is_today = (i == current_day_idx)
            color = active_color if is_today else self.dim_text
            day_surf = self.day_font.render(day, True, color)

            # Center in slot
            day_x = start_x + (i * track_item_w) + (track_item_w / 2) - (day_surf.get_width() / 2)
            surface.blit(day_surf, (int(day_x), int(track_y)))

        # 3. DRAW LED CLOCK
        clock_y = track_y + (12 * self.scale) # INCREASED SPACE HERE
        cursor_x = start_x
        for char in time_str:
            pattern = DIGITS.get(char, DIGITS[' '])
            for row_i, row in enumerate(pattern):
                for col_i, cell in enumerate(row):
                    color = active_color if cell == '#' else self.dim_dot
                    px = int(cursor_x + (col_i * self.spacing))
                    py = int(clock_y + (row_i * self.spacing))
                    pygame.gfxdraw.aacircle(surface, px, py, self.radius, color)
                    pygame.gfxdraw.filled_circle(surface, px, py, self.radius, color)
            cursor_x += 6 * self.spacing

        # 4. DRAW LOCATION NAME (Bold)
        name_lbl = self.name_font.render(self.name, True, active_color)
        name_y = clock_y + total_clock_h + (7 * self.scale)
        surface.blit(name_lbl, (self.rect.centerx - (name_lbl.get_width() // 2), int(name_y)))

        # 5. DRAW DATE
        info_lbl = self.info_font.render(date_str, True, (180, 180, 180))
        info_y = name_y + name_lbl.get_height() + (1.5 * self.scale)
        surface.blit(info_lbl, (self.rect.centerx - (info_lbl.get_width() // 2), int(info_y)))

def main():
    num_display = 4
    scale = 2.5
    theme_name = None  # resolved after loading config

    # Parse args: mclocks [1|2|4] [theme]
    args = sys.argv[1:]
    for arg in args:
        if arg in ("1", "2", "4"):
            num_display = int(arg)
            scale = {1: 6.0, 2: 4.0, 4: 2.5}[num_display]
        elif arg in THEMES:
            theme_name = arg

    # Load config
    all_locations, config_theme = load_config()

    # Theme priority: CLI arg > config default > built-in default
    if theme_name is None:
        theme_name = config_theme if config_theme in THEMES else DEFAULT_THEME
    theme = THEMES[theme_name]

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("mclocks")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    active_locations = all_locations[:num_display]
    panes = []

    for i, (name, tz) in enumerate(active_locations):
        if num_display == 4:
            w, h = WIDTH // 2, HEIGHT // 2
            # Column-major order: 1=top-left, 2=bottom-left, 3=top-right, 4=bottom-right
            col = i // 2
            row = i % 2
            x, y = col * w, row * h
        elif num_display == 2:
            w, h = WIDTH, HEIGHT // 2
            x, y = 0, i * h
        else:  # 1
            w, h = WIDTH, HEIGHT
            x, y = 0, 0
        panes.append(MClockPane(name, tz, (x, y, w, h), scale, theme))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()

        screen.fill(theme["background"])
        for pane in panes:
            pane.draw(screen)

        if num_display > 1:
            div_c = (40, 40, 40)
            pygame.draw.line(screen, div_c, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 1)
            if num_display == 4:
                pygame.draw.line(screen, div_c, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 1)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()