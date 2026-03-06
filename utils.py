# ==================== YARDIMCI FONKSİYONLAR ====================
from datetime import datetime
from config import IRAQ_TZ

def get_iraq_time():
    return datetime.now(IRAQ_TZ)

def format_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M")

def split_message(text, max_length=4096):
    """Uzun mesajları böl"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break
        
        split_at = text[:max_length].rfind('\n')
        if split_at == -1:
            split_at = max_length
        
        parts.append(text[:split_at])
        text = text[split_at:]
    
    return parts
