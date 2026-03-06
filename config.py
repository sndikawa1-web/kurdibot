# ==================== AYARLAR ====================
import os
from datetime import timezone, timedelta

# Telegram
TOKEN = os.environ.get('BOT_TOKEN')
GROUP_ID = int(os.environ.get('GROUP_ID', 0))

# Irak Saati
IRAQ_TZ = timezone(timedelta(hours=3))
