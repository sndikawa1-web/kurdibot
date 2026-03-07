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

# Premium Emoji ID'leri (Telegram'dan almanız gereken ID'ler)
EMOJI_CONFIG = {
    # Diamond 1-10
    1: {"emoji_id": "5367422806881622129", "title": "Diamond 💎"},
    2: {"emoji_id": "5367422806881622130", "title": "Diamond 💎"},
    3: {"emoji_id": "5367422806881622131", "title": "Diamond 💎"},
    4: {"emoji_id": "5367422806881622132", "title": "Diamond 💎"},
    5: {"emoji_id": "5367422806881622133", "title": "Diamond 💎"},
    6: {"emoji_id": "5367422806881622134", "title": "Diamond 💎"},
    7: {"emoji_id": "5367422806881622135", "title": "Diamond 💎"},
    8: {"emoji_id": "5367422806881622136", "title": "Diamond 💎"},
    9: {"emoji_id": "5367422806881622137", "title": "Diamond 💎"},
    10: {"emoji_id": "5367422806881622138", "title": "Diamond 💎"},
    
    # Pro 11-19
    11: {"emoji_id": "5367422806881622139", "title": "Pro ⚡"},
    12: {"emoji_id": "5367422806881622140", "title": "Pro ⚡"},
    13: {"emoji_id": "5367422806881622141", "title": "Pro ⚡"},
    14: {"emoji_id": "5367422806881622142", "title": "Pro ⚡"},
    15: {"emoji_id": "5367422806881622143", "title": "Pro ⚡"},
    16: {"emoji_id": "5367422806881622144", "title": "Pro ⚡"},
    17: {"emoji_id": "5367422806881622145", "title": "Pro ⚡"},
    18: {"emoji_id": "5367422806881622146", "title": "Pro ⚡"},
    19: {"emoji_id": "5367422806881622147", "title": "Pro ⚡"},
    
    # Pro Leader 20-29 (iki emoji)
    20: {"emoji_id": ["5367422806881622148", "5367422806881622149"], "title": "Pro Leader 👑⚡"},
    21: {"emoji_id": ["5367422806881622150", "5367422806881622151"], "title": "Pro Leader 👑⚡"},
    22: {"emoji_id": ["5367422806881622152", "5367422806881622153"], "title": "Pro Leader 👑⚡"},
    23: {"emoji_id": ["5367422806881622154", "5367422806881622155"], "title": "Pro Leader 👑⚡"},
    24: {"emoji_id": ["5367422806881622156", "5367422806881622157"], "title": "Pro Leader 👑⚡"},
    25: {"emoji_id": ["5367422806881622158", "5367422806881622159"], "title": "Pro Leader 👑⚡"},
    26: {"emoji_id": ["5367422806881622160", "5367422806881622161"], "title": "Pro Leader 👑⚡"},
    27: {"emoji_id": ["5367422806881622162", "5367422806881622163"], "title": "Pro Leader 👑⚡"},
    28: {"emoji_id": ["5367422806881622164", "5367422806881622165"], "title": "Pro Leader 👑⚡"},
    29: {"emoji_id": ["5367422806881622166", "5367422806881622167"], "title": "Pro Leader 👑⚡"},
    
    # King 30-39
    30: {"emoji_id": "5367422806881622168", "title": "King 👑"},
    31: {"emoji_id": "5367422806881622169", "title": "King 👑"},
    32: {"emoji_id": "5367422806881622170", "title": "King 👑"},
    33: {"emoji_id": "5367422806881622171", "title": "King 👑"},
    34: {"emoji_id": "5367422806881622172", "title": "King 👑"},
    35: {"emoji_id": "5367422806881622173", "title": "King 👑"},
    36: {"emoji_id": "5367422806881622174", "title": "King 👑"},
    37: {"emoji_id": "5367422806881622175", "title": "King 👑"},
    38: {"emoji_id": "5367422806881622176", "title": "King 👑"},
    39: {"emoji_id": "5367422806881622177", "title": "King 👑"},
    
    # Dragon 40-49
    40: {"emoji_id": "5367422806881622178", "title": "Dragon 🐉"},
    41: {"emoji_id": "5367422806881622179", "title": "Dragon 🐉"},
    42: {"emoji_id": "5367422806881622180", "title": "Dragon 🐉"},
    43: {"emoji_id": "5367422806881622181", "title": "Dragon 🐉"},
    44: {"emoji_id": "5367422806881622182", "title": "Dragon 🐉"},
    45: {"emoji_id": "5367422806881622183", "title": "Dragon 🐉"},
    46: {"emoji_id": "5367422806881622184", "title": "Dragon 🐉"},
    47: {"emoji_id": "5367422806881622185", "title": "Dragon 🐉"},
    48: {"emoji_id": "5367422806881622186", "title": "Dragon 🐉"},
    49: {"emoji_id": "5367422806881622187", "title": "Dragon 🐉"},
    
    # Myth 50-59 (iki emoji)
    50: {"emoji_id": ["5367422806881622188", "5367422806881622189"], "title": "Myth 🔱✨"},
    51: {"emoji_id": ["5367422806881622190", "5367422806881622191"], "title": "Myth 🔱✨"},
    52: {"emoji_id": ["5367422806881622192", "5367422806881622193"], "title": "Myth 🔱✨"},
    53: {"emoji_id": ["5367422806881622194", "5367422806881622195"], "title": "Myth 🔱✨"},
    54: {"emoji_id": ["5367422806881622196", "5367422806881622197"], "title": "Myth 🔱✨"},
    55: {"emoji_id": ["5367422806881622198", "5367422806881622199"], "title": "Myth 🔱✨"},
    56: {"emoji_id": ["5367422806881622200", "5367422806881622201"], "title": "Myth 🔱✨"},
    57: {"emoji_id": ["5367422806881622202", "5367422806881622203"], "title": "Myth 🔱✨"},
    58: {"emoji_id": ["5367422806881622204", "5367422806881622205"], "title": "Myth 🔱✨"},
    59: {"emoji_id": ["5367422806881622206", "5367422806881622207"], "title": "Myth 🔱✨"},
    
    # King Dragon 60-70
    60: {"emoji_id": "5367422806881622208", "title": "King Dragon 👑🐉"},
    61: {"emoji_id": "5367422806881622209", "title": "King Dragon 👑🐉"},
    62: {"emoji_id": "5367422806881622210", "title": "King Dragon 👑🐉"},
    63: {"emoji_id": "5367422806881622211", "title": "King Dragon 👑🐉"},
    64: {"emoji_id": "5367422806881622212", "title": "King Dragon 👑🐉"},
    65: {"emoji_id": "5367422806881622213", "title": "King Dragon 👑🐉"},
    66: {"emoji_id": "5367422806881622214", "title": "King Dragon 👑🐉"},
    67: {"emoji_id": "5367422806881622215", "title": "King Dragon 👑🐉"},
    68: {"emoji_id": "5367422806881622216", "title": "King Dragon 👑🐉"},
    69: {"emoji_id": "5367422806881622217", "title": "King Dragon 👑🐉"},
    70: {"emoji_id": "5367422806881622218", "title": "King Dragon 👑🐉"},
}
