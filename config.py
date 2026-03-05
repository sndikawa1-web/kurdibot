# ==================== AYARLAR ====================
import os
from datetime import timezone, timedelta

# Telegram
TOKEN = os.environ.get('BOT_TOKEN')
GROUP_ID = int(os.environ.get('GROUP_ID', 0))

# Irak Saati
IRAQ_TZ = timezone(timedelta(hours=3))

# Seviye Sistemi
LEVEL_FORMULA = {
    'easy': {'max_level': 15, 'xp_per_level': 200},
    'medium': {'max_level': 30, 'xp_per_level': 300},
    'hard': {'xp_per_level': 500}
}
