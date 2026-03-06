# ==================== SEVİYE SİSTEMİ ====================
import json
import os
from datetime import datetime
from config import IRAQ_TZ

class LevelSystem:
    def __init__(self, db):
        self.db = db
        self.levels_file = 'levels.json'
    
    def calculate_level(self, xp):
        """XP'ye göre level hesapla"""
        if xp < 3000:
            return 1 + (xp // 200)
        elif xp < 9000:
            return 15 + ((xp - 3000) // 300)
        else:
            return 30 + ((xp - 9000) // 500)
    
    def get_xp_for_level(self, level):
        if level <= 15:
            return (level - 1) * 200
        elif level <= 30:
            return 3000 + (level - 15) * 300
        else:
            return 9000 + (level - 30) * 500
    
    def get_level_emoji_id(self, level):
        from messages import Messages
        if level <= 5:
            return Messages.LEVEL_EMOJI_IDS['1-5']
        elif level <= 10:
            return Messages.LEVEL_EMOJI_IDS['6-10']
        elif level <= 15:
            return Messages.LEVEL_EMOJI_IDS['11-15']
        elif level <= 20:
            return Messages.LEVEL_EMOJI_IDS['16-20']
        elif level <= 25:
            return Messages.LEVEL_EMOJI_IDS['21-25']
        elif level <= 30:
            return Messages.LEVEL_EMOJI_IDS['26-30']
        elif level <= 40:
            return Messages.LEVEL_EMOJI_IDS['31-40']
        elif level <= 50:
            return Messages.LEVEL_EMOJI_IDS['41-50']
        else:
            return Messages.LEVEL_EMOJI_IDS['51+']
    
    def update_user(self, user_id, username, total_messages):
        """Kullanıcının seviyesini güncelle - DÜZELTİLDİ"""
        user_id_str = str(user_id)
        
        # Dosyayı oku
        try:
            with open(self.levels_file, 'r', encoding='utf-8') as f:
                levels = json.load(f)
        except:
            levels = {}
        
        # XP hesapla
        xp = total_messages * 10
        new_level = self.calculate_level(xp)
        
        # İlk kez kayıt
        if user_id_str not in levels:
            levels[user_id_str] = {
                'user_id': user_id,
                'username': username,
                'level': new_level,
                'xp': xp,
                'total_messages': total_messages,
                'last_update': datetime.now(IRAQ_TZ).isoformat()
            }
            
            with open(self.levels_file, 'w', encoding='utf-8') as f:
                json.dump(levels, f, ensure_ascii=False, indent=2)
            
            # İlk kayıtta level 1'den büyükse bildirim GÖNDER
            return new_level > 1, new_level
        
        # Var olan kayıt
        old_level = levels[user_id_str]['level']
        old_xp = levels[user_id_str]['xp']
        
        # Sadece değişiklik varsa güncelle
        if old_xp != xp or old_level != new_level:
            levels[user_id_str].update({
                'xp': xp,
                'level': new_level,
                'total_messages': total_messages,
                'last_update': datetime.now(IRAQ_TZ).isoformat()
            })
            
            with open(self.levels_file, 'w', encoding='utf-8') as f:
                json.dump(levels, f, ensure_ascii=False, indent=2)
            
            # Level atladıysa bildirim GÖNDER
            return new_level > old_level, new_level
        
        return False, new_level
