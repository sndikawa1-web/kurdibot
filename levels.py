# levels.py
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
    
    def format_level_message(self, username, level):
        title = self.get_level_title(level)
        emoji = self.get_level_emoji(level)
        
        message = f"🎉 دەستخوش {username}! لیفل {level} - {title}"
        
        # Özel level mesajları
        if level == 10:
            message += "\n\n🌟 تۆ گەهشتیە Level 10! Diamond 💎"
        elif level == 20:
            message += "\n\n👑 تۆ گەهشتیە Level 20! Pro Leader"
        elif level == 30:
            message += "\n\n👑 تۆ گەهشتیە Level 30! King"
        elif level == 40:
            message += "\n\n🐉 تۆ گەهشتیە Level 40! Dragon"
        elif level == 50:
            message += "\n\n🔱 تۆ گەهشتیە Level 50! Myth"
        elif level == 60:
            message += "\n\n👑🐉 تۆ گەهشتیە Level 60! King Dragon"
        elif level == 70:
            message += "\n\n🏆 MAX LEVEL! تۆ گەهشتیە Level 70! 🏆"
        
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
