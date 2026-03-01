#!/usr/bin/env python3
# ==============================================================================
#  mclocks @@VERSION@@
#  Copyright (c) 2026 Yu-Sung Chang | MIT License
# ==============================================================================
#
#  Usage: mclocks.py [MODE] [THEME] [OPTIONS]
#
#  Arguments:
#    MODE          1 (single clock), 2 (top/bottom), 4 (2×2 grid)  [Default: 4]
#    THEME         vibrant, warm, fjord                              [Default: vibrant]
#
#  Options:
#    --12h         12-hour format with AM/PM indicator
#    --24h         24-hour format (default)
#    -h, --help    Display this help and exit
#    -v, --version Display version and exit
#
# ==============================================================================

import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import pygame.gfxdraw
import datetime
import pytz
import configparser
import pathlib

VERSION = "@@VERSION@@"

# --- BASE CONFIGURATION ---
WIDTH, HEIGHT = 800, 480    # Standard Raspberry Pi display size (5")
BASE_DIGIT_HEIGHT = 7       # Number of rows in digit patterns (fixed by DIGITS dict)
BASE_DOT_SPACING = 2.5      # Spacing between clock dots at scale=1
BASE_DOT_RADIUS = 1         # Radius of clock dots at scale=1
BASE_LINE_SPACE = 7         # Vertical gap between day, clock, and info sections at scale=1
BASE_DAY_FONT_SIZE = 5
BASE_INFO_FONT_SIZE = 7
SCALE_FACTORS = {1: 5.5, 2: 4.0, 4: 2.75}  # Scale for different display modes (1, 2, or 4 panes)
FPS = 5

# --- MOCK TIME UTILITY (for testing without relying on system clock) 
def get_mock_time(tz):
    # Construct a fixed point in time
    dt = datetime.datetime(2026, 2, 28, 11, 7, 45)
    seoul_tz = pytz.timezone("Asia/Seoul")
    seoul_time = seoul_tz.localize(dt)
    return seoul_time.astimezone(tz)

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
    "cold": {
        "background": (6, 10, 22),
        "dim_dot":  (12, 22, 46),
        "dim_text": (20, 36, 68),
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
        link = os.readlink('/etc/localtime')
        if 'zoneinfo/' in link:
            return link.split('zoneinfo/')[-1]
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
    time_format = 24
    if config.has_section('settings'):
        if config.has_option('settings', 'default_theme'):
            default_theme = config.get('settings', 'default_theme').strip()
        if config.has_option('settings', 'time_format'):
            val = config.get('settings', 'time_format').strip()
            if val in ('12', '24'):
                time_format = int(val)

    return resolved, default_theme, time_format

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
    ' ': ["     ",
          "     ",
          "     ",
          "     ",
          "     ",
          "     ",
          "     "],
    ':': ["   ",
          " # ",
          "   ",
          "   ",
          "   ",
          " # ",
          "   "],
}

def get_circadian_color(hour, circadian_map):
    for i in range(len(circadian_map) - 1):
        if circadian_map[i][0] <= hour < circadian_map[i+1][0]:
            return circadian_map[i][1]
    return circadian_map[-1][1]

class MClockPane:
    def __init__(self, name, timezone, rect, scale, theme, time_format=24):
        self.name = name
        self.tz = pytz.timezone(timezone)
        self.rect = pygame.Rect(rect)
        self.theme = theme
        self.dim_dot = theme["dim_dot"]
        self.dim_text = theme["dim_text"]
        self.time_format = time_format
        self.is_12h = (time_format == 12)

        self.dot_spacing = BASE_DOT_SPACING * scale
        self.dot_radius = int(BASE_DOT_RADIUS * scale)
        line_space = int(BASE_LINE_SPACE * scale)

        # Geometry stored as self.xxx — computed once, used in draw() every frame:
     
        #   start_y             top of content block (vertically centered in rect)
        #   day_item_w          width allocated for each day in the day-track (clock_w / 7)
        #   day_text_y_offset   vertical offset to center day text (accounts for font padding)
        #   clock_x             left edge of clock digits (AM/PM or clock is centered in rect)
        #   clock_y             top of clock dots
        #   clock_w             pixel width of "HH:MM:SS" (' ' placeholder is 5-wide)
        #   ampm_x              left edge of AM/PM (or clock in 24h); clock_x is offset from this by ampm_w
        #   am_y / pm_y         y positions for AM/PM labels (12h only)
        #   info_y              top for the location · date line
        #   info_text_y_offset  vertical offset to center info text (accounts for font padding)
    
        try:
            self.day_font = pygame.font.Font(font_path("JetBrainsMono-ExtraBold.ttf"), int(BASE_DAY_FONT_SIZE * scale))
            self.info_font = pygame.font.Font(font_path("JetBrainsMono-Bold.ttf"), int(BASE_INFO_FONT_SIZE * scale))
        except Exception as e:
            print(f"Error: could not load fonts from {FONT_DIR}: {e}", file=sys.stderr)
            pygame.quit()
            sys.exit(1)

        # This is to calculate actual height of rendered text and the offset between actual and font height
        # Quite a bit of hack, but it is necessary for low resolution displays where font padding can cause significant misalignment
        _day_sample  = self.day_font.render("MON", True, (255, 255, 255))
        _info_sample = self.info_font.render("SEOUL · 2026-02-28", True, (255, 255, 255))
        day_text_height  = _day_sample.get_bounding_rect().height
        info_text_height = _info_sample.get_bounding_rect().height
        self.day_text_y_offset  = -(self.day_font.get_height()  - day_text_height)  // 2
        info_text_y_offset = -(self.info_font.get_height() - info_text_height) // 2

        clock_h = int(BASE_DIGIT_HEIGHT * self.dot_spacing)
        ampm_w = int(self.day_font.size("AM")[0] + self.dot_spacing) if self.is_12h else 0

        # Pre-computed clock width — ' ' placeholder is 5-wide so all time strings have equal width
        def _clock_w_calc(s):
            return (sum(len(DIGITS.get(c, DIGITS[' '])[0]) for c in s) + len(s) - 1) * self.dot_spacing
        self.clock_w = _clock_w_calc("HH:MM:SS")

        self.ampm_x = self.rect.centerx - int((ampm_w + self.clock_w) // 2)
        self.clock_x = self.ampm_x + ampm_w

        self.day_item_w = self.clock_w / len(DAYS)

        # Vertical layout
        total_h = (day_text_height + line_space + clock_h + line_space + info_text_height)
        self.start_y = self.rect.centery - total_h // 2
        self.clock_y = self.start_y + day_text_height + line_space
        self.info_y  = self.clock_y + clock_h + line_space + info_text_y_offset

        # AM/PM y positions (12h mode only)
        if self.is_12h:
            half_h = clock_h / 2
            font_h = self.day_font.get_height()
            self.am_y = int(self.clock_y + half_h / 2 - font_h / 2)
            self.pm_y = int(self.clock_y + half_h + half_h / 2 - font_h / 2)

    def draw(self, surface):
        now = datetime.datetime.now(self.tz)
        # now = get_mock_time(self.tz) # For testing with a fixed time regardless of system clock

        if self.is_12h:
            time_str = now.strftime("%I:%M:%S")
            if time_str.startswith('0'):
                time_str = ' ' + time_str[1:]
            is_pm = now.hour >= 12
        else:
            time_str = now.strftime("%H:%M:%S")
            is_pm = False
        date_str = now.strftime("%Y-%m-%d").upper()
        current_day_idx = now.weekday()
        active_color = get_circadian_color(now.hour, self.theme["circadian"])

        # 2. DRAW BOLD DAY-TRACK — aligned to clock digits
        day_y = self.start_y + self.day_text_y_offset
        for i, day in enumerate(DAYS):
            is_today = (i == current_day_idx)
            color = active_color if is_today else self.dim_text
            day_surf = self.day_font.render(day, True, color)
            day_x = self.clock_x + int((i * self.day_item_w) + (self.day_item_w / 2) - (day_surf.get_width() / 2))
            surface.blit(day_surf, (int(day_x), int(day_y)))

        # 3. DRAW AM/PM indicator (12h mode only)
        if self.is_12h:
            am_color = self.dim_text if is_pm else active_color
            pm_color = active_color if is_pm else self.dim_text
            am_surf = self.day_font.render("AM", True, am_color)
            pm_surf = self.day_font.render("PM", True, pm_color)
            surface.blit(am_surf, (self.ampm_x, self.am_y))
            surface.blit(pm_surf, (self.ampm_x, self.pm_y))

        # 4. DRAW LED CLOCK
        dot_y = self.clock_y + int(self.dot_spacing // 2)
        cursor_x = self.clock_x + int(self.dot_spacing // 2)
        for char in time_str:
            pattern = DIGITS.get(char, DIGITS[' '])
            for row_i, row in enumerate(pattern):
                for col_i, cell in enumerate(row):
                    color = active_color if cell == '#' else self.dim_dot
                    px = int(cursor_x + (col_i * self.dot_spacing))
                    py = int(dot_y + (row_i * self.dot_spacing))
                    pygame.gfxdraw.aacircle(surface, px, py, self.dot_radius, color)
                    pygame.gfxdraw.filled_circle(surface, px, py, self.dot_radius, color)
            cursor_x += (len(DIGITS.get(char, DIGITS[' '])[0]) + 1) * self.dot_spacing

        # 5. DRAW LOCATION  ·  DATE (combined line)
        dim_color = tuple(int(c * 0.8) for c in active_color)
        name_surf = self.info_font.render(self.name, True, active_color)
        div_surf  = self.info_font.render(" · ", True, dim_color)
        date_surf = self.info_font.render(date_str, True, dim_color)
        combined_w = name_surf.get_width() + div_surf.get_width() + date_surf.get_width()
        info_x = self.rect.centerx - combined_w // 2
        surface.blit(name_surf, (info_x, self.info_y))
        surface.blit(div_surf,  (info_x + name_surf.get_width(), self.info_y))
        surface.blit(date_surf, (info_x + name_surf.get_width() + div_surf.get_width(), self.info_y))

def usage():
    print(f"mclocks {VERSION} - Multi-timezone world clock for Raspberry Pi displays.", file=sys.stderr)
    print( "Copyright (c) 2026 Yu-Sung Chang. Released under the MIT License.", file=sys.stderr)
    print(file=sys.stderr)
    print( "Usage: mclocks.py [MODE] [THEME] [OPTIONS]", file=sys.stderr)
    print(file=sys.stderr)
    print( "Arguments:", file=sys.stderr)
    print( "  MODE    Display layout: 1 (single), 2 (top/bottom), 4 (2×2 grid)  [Default: 4]", file=sys.stderr)
    print( "  THEME   Color theme: vibrant, warm, fjord                          [Default: vibrant]", file=sys.stderr)
    print(file=sys.stderr)
    print( "Options:", file=sys.stderr)
    print( "  --12h            12-hour format with AM/PM indicator", file=sys.stderr)
    print( "  --24h            24-hour format (default)", file=sys.stderr)
    print( "  -h, --help       Display this help and exit", file=sys.stderr)
    print( "  -v, --version    Display version and exit", file=sys.stderr)

    print(file=sys.stderr)
    print( "Examples:", file=sys.stderr)
    print( "  mclocks.py               # 2×2 grid, vibrant theme", file=sys.stderr)
    print( "  mclocks.py 1 fjord       # Single clock, fjord theme", file=sys.stderr)
    print( "  mclocks.py 2 warm        # Top/bottom, warm theme", file=sys.stderr)
    print( "  mclocks.py 4             # 2×2 grid, vibrant theme", file=sys.stderr)


def main():
    num_display = 4
    theme_name = None  # resolved after loading config

    # Parse args: mclocks [1|2|4] [theme] [--screenshot] [-v] [-h]
    args = sys.argv[1:]

    if any(a in ('-v', '--version') for a in args):
        print(f"mclocks {VERSION}")
        sys.exit(0)

    if any(a in ('-h', '--help') for a in args):
        usage()
        sys.exit(0)

    screenshot = '--screenshot' in args
    time_format = None
    for arg in args:
        if arg in ("1", "2", "4"):
            num_display = int(arg)
        elif arg in THEMES:
            theme_name = arg
        elif arg == '--12h':
            time_format = 12
        elif arg == '--24h':
            time_format = 24

    scale = SCALE_FACTORS[num_display]

    # Load config
    all_locations, config_theme, config_time_format = load_config()
    if time_format is None:
        time_format = config_time_format

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
        panes.append(MClockPane(name, tz, (x, y, w, h), scale, theme, time_format))

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
        if screenshot:
            base_name = "screenshot"
            extension = ".png"
            counter = 1
    
            # 1. & 2. Verify if the file exists and increment the postfix
            filename = f"{base_name}{extension}"
            while os.path.exists(filename):
                filename = f"{base_name}_{counter}{extension}"
                counter += 1
    
            pygame.image.save(screen, filename)
            pygame.quit(); sys.exit(0)

        clock.tick(FPS)

if __name__ == "__main__":
    main()