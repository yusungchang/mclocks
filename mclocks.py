#!/usr/bin/env python3
# mclocks @@VERSION@@
# A pygame-based multi-timezone world clock for Raspberry Pi displays

import pygame
import pygame.gfxdraw
import datetime
import pytz
import sys
import os

# --- BASE CONFIGURATION ---
WIDTH, HEIGHT = 800, 480  
BASE_SPACING = 2.5         
BASE_RADIUS = 1           
FPS = 10

ALL_LOCATIONS = [
    ("SEOUL", "Asia/Seoul"), 
    ("SINGAPORE", "Asia/Singapore"),
    ("SAN FRANCISCO", "America/Los_Angeles"), 
    ("NEW YORK", "America/New_York")
]

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

CIRCADIAN_MAP = [
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

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

# --- FONT PATH ---
# Resolve fonts relative to this script's location (works both installed and local)
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FONT_DIR = os.path.join(SCRIPT_DIR, "fonts")

def font_path(filename):
    return os.path.join(FONT_DIR, filename)

def get_circadian_color(hour):
    for i in range(len(CIRCADIAN_MAP) - 1):
        if CIRCADIAN_MAP[i][0] <= hour < CIRCADIAN_MAP[i+1][0]:
            return CIRCADIAN_MAP[i][1]
    return CIRCADIAN_MAP[-1][1]

class MClockPane:
    def __init__(self, name, timezone, rect, scale):
        self.name = name
        self.tz = pytz.timezone(timezone)
        self.rect = pygame.Rect(rect)
        self.scale = scale
        self.spacing = BASE_SPACING * scale
        self.radius = int(BASE_RADIUS * scale)
        self.dim_dot = (25, 25, 25)
        self.dim_text = (65, 65, 65)
        
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
        active_color = get_circadian_color(now.hour)
        
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
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "2":
            num_display = 2
            scale = 4.0
        elif sys.argv[1] == "4":
            num_display = 4
            scale = 2.5

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("mclocks")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    active_locations = ALL_LOCATIONS[:num_display]
    panes = []

    for i, (name, tz) in enumerate(active_locations):
        if num_display == 4:
            w, h = WIDTH // 2, HEIGHT // 2
            x, y = (i % 2) * w, (i // 2) * h
        else:
            w, h = WIDTH, HEIGHT // 2
            x, y = 0, i * h
        panes.append(MClockPane(name, tz, (x, y, w, h), scale))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); sys.exit()

        screen.fill((5, 5, 5))
        for pane in panes:
            pane.draw(screen)

        div_c = (40, 40, 40)
        pygame.draw.line(screen, div_c, (0, HEIGHT//2), (WIDTH, HEIGHT//2), 1)
        if num_display == 4:
            pygame.draw.line(screen, div_c, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 1)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()