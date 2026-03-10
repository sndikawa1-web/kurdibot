# levels.py - VIP/SVIP SİSTEMLİ SON VERSİYON
from config import EMOJI_CONFIG

class LevelSystem:
    def __init__(self):
        self.emoji_config = EMOJI_CONFIG
        # ÖZEL EMOJİLERİNİZ
        self.emoji1 = "5357136605498857329"  # Baştaki ve sondaki emoji
        self.emoji2 = "5998897065613071275"  # Level yanındaki emoji
        
        # VIP/SVIP için özel emojiler
        self.vip_emoji_start = "5231294849705064103"  # VIP başlangıç emojisi
        self.vip_emoji_end = "5296642330437107668"    # VIP bitiş emojisi
    
    def get_level_title(self, level):
        """Level 70'e kadar normal ünvanlar"""
        if 1 <= level <= 10:
            return "Diamond 💎"
        elif 11 <= level <= 19:
            return "Pro ⚡"
        elif 20 <= level <= 29:
            return "Pro Leader 👑⚡"
        elif 30 <= level <= 39:
            return "King 👑"
        elif 40 <= level <= 49:
            return "Dragon 🐉"
        elif 50 <= level <= 59:
            return "Myth 🔱✨"
        elif 60 <= level <= 70:
            return "King Dragon 👑🐉"
        elif 71 <= level <= 80:
            return f"VIP {level-70} 👑💎"  # VIP 1-10
        elif 81 <= level <= 90:
            return f"SVIP {level-80} ⚡👑"  # SVIP 1-10
        else:
            return "MAX LEVEL 👑🔥"
    
    def get_level_tag(self, level):
        """Level'a göre etiket (tag) döndür"""
        if 1 <= level <= 10:
            return "💎 Diamond"
        elif 11 <= level <= 19:
            return "⚡ Pro"
        elif 20 <= level <= 29:
            return "👑⚡ Pro Leader"
        elif 30 <= level <= 39:
            return "👑 King"
        elif 40 <= level <= 49:
            return "🐉 Dragon"
        elif 50 <= level <= 59:
            return "🔱✨ Myth"
        elif 60 <= level <= 70:
            return "👑🐉 King Dragon"
        elif 71 <= level <= 80:
            return f"VIP {level-70}"
        elif 81 <= level <= 90:
            return f"SVIP {level-80}"
        else:
            return "MAX LEVEL"
    
    def get_level_emoji(self, level):
        """Level'a göre config'deki emoji ID'sini döndür"""
        if level in self.emoji_config:
            return self.emoji_config[level]["emoji_id"]
        return None
    
    def format_level_message(self, mention, level, xp):
        """Level atlama mesajı - TIKLANABİLİR İSİMLİ"""
        title = self.get_level_title(level)
        
        # Level 70'den sonra VIP/SVIP özel emojileri kullan
        if level >= 71:
            emoji1_html = f'<tg-emoji emoji-id="{self.vip_emoji_start}">👑</tg-emoji>'
            emoji2_html = f'<tg-emoji emoji-id="{self.vip_emoji_end}">⭐</tg-emoji>'
        else:
            # Normal level emojileri
            emoji1_html = f'<tg-emoji emoji-id="{self.emoji1}">⭐</tg-emoji>'
            emoji2_html = f'<tg-emoji emoji-id="{self.emoji2}">⭐</tg-emoji>'
        
        # TAM İSTEDİĞİNİZ FORMAT
        message = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"{emoji1_html} {mention} {emoji1_html}\n"
            f"Level {emoji2_html} {level} {emoji2_html} {title}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )
        
        return message
    
    def format_top_list(self, top_users):
        """Lider tablosu"""
        if not top_users:
            return "🏆 لیستا ڤاله‌یه - هێچ کاربەر نینە"
        
        message = "🏆 لیستا ڕیزبه‌ندیان\n\n"
        
        for i, user in enumerate(top_users[:10], 1):
            user_id, username, first_name, xp, level, msg_count = user
            name = f"@{username}" if username else first_name
            title = self.get_level_title(level)
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += f"{medal} {name}\n"
            message += f"   • Level {level} - {title}\n"
            message += f"   • XP: {xp} | نامە: {msg_count}\n\n"
        
        return message
