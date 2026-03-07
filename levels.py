# levels.py - GÜNCELLENMİŞ VERSİYON (Level atlama bildirimi düzenlendi)
from config import EMOJI_CONFIG

class LevelSystem:
    def __init__(self):
        self.emoji_config = EMOJI_CONFIG
    
    def get_level_emoji(self, level):
        if level in self.emoji_config:
            return self.emoji_config[level]["emoji_id"]
        return None
    
    def get_level_title(self, level):
        if level in self.emoji_config:
            return self.emoji_config[level]["title"]
        
        if level <= 10:
            return "Diamond 💎"
        elif level <= 19:
            return "Pro ⚡"
        elif level <= 29:
            return "Pro Leader 👑⚡"
        elif level <= 39:
            return "King 👑"
        elif level <= 49:
            return "Dragon 🐉"
        elif level <= 59:
            return "Myth 🔱✨"
        else:
            return "King Dragon 👑🐉"
    
    def format_level_message(self, username, level, xp):
        """Level atlama mesajını formatla - YENİ FORMAT"""
        title = self.get_level_title(level)
        emoji = self.get_level_emoji(level)
        
        # Sonraki level için gereken XP
        next_level_xp = (level * 100)
        current_xp = xp
        xp_needed = next_level_xp - current_xp
        messages_needed = xp_needed // 10  # Her mesaj 10 XP
        
        # Premium emoji HTML formatı
        emoji_html = ""
        if emoji:
            if isinstance(emoji, list):
                # İki emoji yan yana
                emoji_html = f'<tg-emoji emoji-id="{emoji[0]}">⭐</tg-emoji><tg-emoji emoji-id="{emoji[1]}">⭐</tg-emoji>'
            else:
                # Tek emoji
                emoji_html = f'<tg-emoji emoji-id="{emoji}">⭐</tg-emoji>'
        
        # YENİ FORMAT - tam istediğiniz gibi
        if level == 70:
            message = (
                f"{username}\n"
                f"🎉🎉 دەستخوش لیفل زێدەبو 🎉🎉\n"
                f"{title} = {level} {emoji_html}\n"
                f"🏆 MAX LEVEL! تۆ گەهشتیە Level 70! 🏆"
            )
        else:
            message = (
                f"{username}\n"
                f"🎉🎉 دەستخوش لیفل زێدەبو 🎉🎉\n"
                f"{title} = {level} {emoji_html}\n"
                f"📊 بۆ لیفلەکێ نڤ: {messages_needed} mesaj"
            )
        
        return message, emoji
    
    def format_top_list(self, top_users):
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
