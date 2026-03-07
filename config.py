# config.py
import os
from datetime import time

# Railway environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ALLOWED_GROUP_ID = int(os.environ.get('GROUP_ID', '-1001234567890'))

# Veritabanı
DB_NAME = "badini_bot.db"

# Zaman ayarları (Irak saati - UTC+3)
IRAQ_TIMEZONE = 3
DAILY_REPORT_TIME = time(0, 0, 0)  # Gece 00:00
WEEKLY_REPORT_DAY = 0  # Pazartesi

# Level sistemi
XP_PER_MESSAGE = 10
MAX_LEVEL = 70

# SİZİN PREMIUM EMOJİ ID'LERİNİZ (aynı ID'yi tüm level'lara verdim, siz değiştirin)
EMOJI_CONFIG = {
    # Diamond level 1-10
    1: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    2: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    3: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    4: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    5: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    6: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    7: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    8: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    9: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    10: {"emoji_id": "5258112758645282249", "title": "Diamond 💎"},
    
    # Pro level 11-19
    11: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    12: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    13: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    14: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    15: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    16: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    17: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    18: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    19: {"emoji_id": "5258112758645282249", "title": "Pro ⚡"},
    
    # Pro Leader level 20-29 (iki emoji yan yana)
    20: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    21: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    22: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    23: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    24: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    25: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    26: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    27: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    28: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    29: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Pro Leader 👑⚡"},
    
    # King level 30-39
    30: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    31: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    32: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    33: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    34: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    35: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    36: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    37: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    38: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    39: {"emoji_id": "5258112758645282249", "title": "King 👑"},
    
    # Dragon level 40-49
    40: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    41: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    42: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    43: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    44: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    45: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    46: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    47: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    48: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    49: {"emoji_id": "5258112758645282249", "title": "Dragon 🐉"},
    
    # Myth level 50-59 (iki emoji yan yana)
    50: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    51: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    52: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    53: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    54: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    55: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    56: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    57: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    58: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    59: {"emoji_id": ["5258112758645282249", "5258112758645282249"], "title": "Myth 🔱✨"},
    
    # King Dragon level 60-70
    60: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    61: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    62: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    63: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    64: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    65: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    66: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    67: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    68: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    69: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
    70: {"emoji_id": "5258112758645282249", "title": "King Dragon 👑🐉"},
}
