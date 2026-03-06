# ==================== SEVİYE SİSTEMİ ====================
import json
import os
import logging
from datetime import datetime
from config import IRAQ_TZ

logger = logging.getLogger(__name__)

class LevelSystem:
    def __init__(self, db):
        self.db = db
        self.levels_file = 'levels.json'
        logger.debug(f"LevelSystem başlatıldı, dosya: {self.levels_file}")
    
    def calculate_level(self, xp):
        """XP'ye göre level hesapla (15'den sonra zorlaşır)"""
        if xp < 3000:  # Level 1-15 (her level 200 XP)
            return 1 + (xp // 200)
        elif xp < 9000:  # Level 15-30 (her level 300 XP)
            return 15 + ((xp - 3000) // 300)
        else:  # Level 30+ (her level 500 XP)
            return 30 + ((xp - 9000) // 500)
    
    def get_xp_for_level(self, level):
        """Bir level için gereken XP'yi hesapla"""
        if level <= 15:
            return (level - 1) * 200
        elif level <= 30:
            return 3000 + (level - 15) * 300
        else:
            return 9000 + (level - 30) * 500
    
    def get_level_emoji_id(self, level):
        """Seviyeye göre emoji ID'si döndür"""
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
        """Kullanıcının seviyesini güncelle - VERİLERİ KORUR"""
        user_id_str = str(user_id)
        
        logger.debug(f"📊 update_user başladı: user={user_id}, total={total_messages}")
        
        # Dosyayı oku (yoksa boş dict oluşur)
        try:
            with open(self.levels_file, 'r', encoding='utf-8') as f:
                levels = json.load(f)
            logger.debug(f"📁 levels.json okundu, {len(levels)} kayıt var")
        except FileNotFoundError:
            logger.debug(f"📁 levels.json bulunamadı, yeni oluşturulacak")
            levels = {}
        except Exception as e:
            logger.error(f"❌ levels.json okuma hatası: {e}")
            levels = {}
        
        # XP hesapla
        xp = total_messages * 10
        new_level = self.calculate_level(xp)
        logger.debug(f"📊 XP={xp}, new_level={new_level}")
        
        # İlk kez kayıt
        if user_id_str not in levels:
            logger.debug(f"🆕 Yeni kullanıcı kaydı: {user_id}")
            levels[user_id_str] = {
                'user_id': user_id,
                'username': username,
                'level': new_level,
                'xp': xp,
                'total_messages': total_messages,
                'last_update': datetime.now(IRAQ_TZ).isoformat()
            }
            
            try:
                with open(self.levels_file, 'w', encoding='utf-8') as f:
                    json.dump(levels, f, ensure_ascii=False, indent=2)
                logger.debug(f"✅ Yeni kullanıcı kaydedildi")
            except Exception as e:
                logger.error(f"❌ Kayıt hatası: {e}")
            
            result = new_level > 1, new_level
            logger.debug(f"📤 Dönüş: {result}")
            return result
        
        # Var olan kayıt
        old_level = levels[user_id_str]['level']
        old_xp = levels[user_id_str]['xp']
        logger.debug(f"📊 Eski: level={old_level}, xp={old_xp}")
        
        # Sadece değişiklik varsa güncelle
        if old_xp != xp or old_level != new_level:
            logger.debug(f"🔄 Güncelleme yapılıyor")
            levels[user_id_str].update({
                'xp': xp,
                'level': new_level,
                'total_messages': total_messages,
                'last_update': datetime.now(IRAQ_TZ).isoformat()
            })
            
            try:
                with open(self.levels_file, 'w', encoding='utf-8') as f:
                    json.dump(levels, f, ensure_ascii=False, indent=2)
                logger.debug(f"✅ Güncelleme kaydedildi")
            except Exception as e:
                logger.error(f"❌ Güncelleme hatası: {e}")
            
            result = new_level > old_level, new_level
            logger.debug(f"📤 Dönüş: {result}")
            return result
        
        logger.debug(f"📤 Değişiklik yok")
        return False, new_level
    
    def get_user_rank(self, user_id):
        """Kullanıcının sıralamasını bul"""
        user_id_str = str(user_id)
        
        try:
            with open(self.levels_file, 'r', encoding='utf-8') as f:
                levels = json.load(f)
        except:
            return None, 0
        
        # Tüm kullanıcıları XP'ye göre sırala
        sorted_users = sorted(levels.items(), key=lambda x: x[1]['xp'], reverse=True)
        
        for i, (uid, data) in enumerate(sorted_users, 1):
            if uid == user_id_str:
                return i, len(sorted_users)
        
        return None, len(sorted_users)
    
    def get_user_data(self, user_id):
        """Kullanıcının seviye verilerini getir"""
        try:
            with open(self.levels_file, 'r', encoding='utf-8') as f:
                levels = json.load(f)
            return levels.get(str(user_id))
        except:
            return None
    
    def get_top_users(self, limit=10):
        """En yüksek seviyedeki kullanıcıları getir"""
        try:
            with open(self.levels_file, 'r', encoding='utf-8') as f:
                levels = json.load(f)
        except:
            return []
        
        # XP'ye göre sırala
        sorted_users = sorted(levels.items(), key=lambda x: x[1]['xp'], reverse=True)[:limit]
        
        result = []
        users = self.db.get_all_users()
        
        for user_id, data in sorted_users:
            user_data = users.get(user_id, {})
            username = user_data.get('username')
            display = f"@{username}" if username else user_data.get('first_name', '?')
            result.append((display, data['level'], data['xp'], data['total_messages']))
        
        return result
