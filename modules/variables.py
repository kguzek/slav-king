"""Global game variable definitions."""

from configparser import ConfigParser
import random

# Game variables
score = 0
money_count = 0
wanted_level = 0
fps = 0
shot_cooldown_time_passed = 0
shot_cooldown = 0
time_passed_since_last_cop_spawned = 0
cop_amount = 1
win_x = 0
pause_menu = "main"
previous_pause_menu = ""
cop_hovering_over: None | tuple[int, int] = None
cop_spawn_delay = random.randint(500, 2500) / 1000

run = True
firing = False
paused = False
selected_gun = None
slider_engaged = False
cops = []
bullets = []
drops = []

settings: ConfigParser
