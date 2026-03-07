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
    
    def format_level_message(self, user_name, old_level, new_level):
        title = self.get_level_title(new_level)
        
        # Badînî çeviri - sizin verdiğiniz formatta
        if new_level <= 10:
            message = f"🎉 دەستخوش {user_name} گەهشتیە لیفل {new_level}! رتبە {title}"
        elif new_level <= 19:
            message = f"🎉 دەستخوش {user_name} گەهشتیە لیفل {new_level}! رتبە {title}"
        elif new_level <= 29:
            message = f"🎉 دەستخوش {user_name} گەهشتیە لیفل {new_level}! رتبە {title}"
        elif new_level <= 39:
            message = f"🎉 دەستخوش {user_name} گەهشتیە لیفل {new_level}! رتبە {title}"
        elif new_level <= 49:
            message = f"🎉 دەستخوش {user_name} گەهشتیە لیفل {new_level}! رتبە {title}"
        elif new_level <= 59:
            message = f"🎉 دەستخوش {user_name} گەهشتیە لیفل {new_level}! رتبە {title}"
        else:
            message = f"🎉 دەستخوش {user_name} گەهشتیە لیفل {new_level}! رتبە {title}"
        
        return message
    
    def format_top_list(self, top_users):
        if not top_users:
            return "📊 لیستا ڕیزبه‌ندیان ڤاله‌ یه"
        
        message = "🏆 **لیستا ڕیزبه‌ندیان ێکی**\n\n"
        
        for i, user in enumerate(top_users[:10], 1):
            user_id, username, first_name, xp, level, msg_count = user
            name = f"@{username}" if username else first_name
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📌"
            message += f"{medal} {i}. **{name}**\n"
            message += f"   • Level {level}\n"
            message += f"   • XP: {xp} | نامه‌: {msg_count}\n\n"
        
        return message
