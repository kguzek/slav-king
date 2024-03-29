"""Constant variable definitions for Slav King."""

# Pygame window
WIN_WIDTH = 960
WIN_HEIGHT = 540

# Resources
IMAGE_DIR = "data/images/"
SPRITE_DIR = "data/sprites/"
AUDIO_DIR = "data/audio/"

PAUSE_INSTRUCTIONS = {
    "main": "unpause",
    "volume": "options",
    "options": "main",
    "dev": "options",
    "shop": "prev",
    "quit": "main",
}

LOOT_TABLE = {
    "money": {"drop_chance": 3, "pickup_amount_multiplier": 4},
    "ammo_light": {"drop_chance": 4, "pickup_amount_multiplier": 2},
    "ammo_heavy": {"drop_chance": 1, "pickup_amount_multiplier": 1},
}

STORE_ICON_PADDING = 24

# Cheats - Change these :D
GOD_MODE = False
INFINITE_AMMO = False

# After 50 drops, the oldest ones will start to disappear
MAX_RENDERED_DROPS = 50

FRAME_WIDTH = 16 * 16
FRAME_HEIGHT = 9 * 16 + 20
FRAME_GAP = 32

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
