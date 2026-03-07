# utils.py
import datetime
import pytz
from config import IRAQ_TIMEZONE

class BadiniTranslations:
    """Badînî dilindeki tüm metinler"""
    
    @staticmethod
    def level_up_message(username, level, title):
        if level <= 10:
            return f"🎉 دەستخوش @{username} گەهشتیە لیفل {level}! رتبە {title}"
        elif level <= 19:
            return f"🎉 دەستخوش @{username} گەهشتیە لیفل {level}! رتبە {title}"
        elif level <= 29:
            return f"🎉 دەستخوش @{username} گەهشتیە لیفل {level}! رتبە {title}"
        elif level <= 39:
            return f"🎉 دەستخوش @{username} گەهشتیە لیفل {level}! رتبە {title}"
        elif level <= 49:
            return f"🎉 دەستخوش @{username} گەهشتیە لیفل {level}! رتبە {title}"
        elif level <= 59:
            return f"🎉 دەستخوش @{username} گەهشتیە لیفل {level}! رتبە {title}"
        else:
            return f"🎉 دەستخوش @{username} گەهشتیە لیفل {level}! رتبە {title}"
    
    @staticmethod
    def inactive_24h_report(inactive_list, count=None):
        if not inactive_list:
            return "📊 راپورا 24 سعەتان - هەمی ئاکتیڤن 🎉"
        
        message = "📊 راپورا 24 سعەتان - ئەو کەسێن 24 سعەتاندا نە ئاخفتین:\n\n"
        for user in inactive_list:
            user_id, username, first_name = user
            name = f"@{username}" if username else first_name
            message += f"• {name}\n"
        
        if count:
            message += f"\nئەو کەسێن نە ئاخفتین {count} کەس"
        
        return message
    
    @staticmethod
    def weekly_report(active_users):
        if not active_users:
            return "📅 راپورتا حەڤتیێ ئەندامێن نە ئاکتیڤ"
        
        message = "📅 راپورتا حەڤتیێ - ئەندامێن ئاکتیڤ:\n\n"
        for i, (user_id, msg_count) in enumerate(active_users[:5], 1):
            if i == 1:
                medal = "🥇 gold"
            elif i == 2:
                medal = "🥈 silver"
            elif i == 3:
                medal = "🥉 bronze"
            else:
                medal = f"{i}."
            
            message += f"{medal} User ID: {user_id}\n"
            message += f"   • نامە (حەفتە): {msg_count}\n\n"
        
        return message
    
    @staticmethod
    def top_chatters_report(top_users):
        message = "🗣 کەسێن ڤێ حەڤتیێ دا گەلەک ئاکتیڤ:\n\n"
        for i, user in enumerate(top_users, 1):
            user_id, username, first_name = user[:3]
            name = f"@{username}" if username else first_name
            message += f"{i}. {name}\n"
        
        return message
    
    @staticmethod
    def error_message(error_type="general"):
        errors = {
            "general": "❌ خەلەتیەک چێبی دوبارە هەول بدە",
            "not_admin": "⛔ تنێ ئادمین دشێن ڤی بەشی بکار بینن",
            "wrong_group": "🚫 ئەڤ بوتە تنێ د گروپێ تایبەت دا کار دکەت",
            "no_user": "👤 ئەڤ کەسە نەهاتە دیتن",
            "invalid_format": "⚠️ خەلەتە"
        }
        return errors.get(error_type, errors["general"])
    
    @staticmethod
    def command_descriptions():
        return {
            "level": "📊 /level - لیفلێ خۆ و XP'yê نیشان بدە",
            "stats": "📈 /stats - داتایێن خۆ نیشان بدە",
            "top": "🏆 /top - ئەندامێن بیلیفتا هەرێ بلند",
            "24h": "⏰ /24h - کەسێن 24 سەعتاندا نە ئاخفتین (تەنێ ئادمین)",
            "nadmin": "👑 /nadmin - ڕێڤەبەرێن نوی بیبینە و رۆژانە بکە (تەنێ ئادمین)",
            "help": "❓ /help - هەمی فرمانان نیشان بدە"
        }
    
    @staticmethod
    def new_admins_message(new_admins):
        if not new_admins:
            return "👑 ڕێڤەبەرێن نوی نەهاتنە دیتن"
        
        message = "👑 **ڕێڤەبەرێن نوی هاتنە دیتن و زیادکرن:**\n\n"
        for admin in new_admins:
            user_id, username, first_name = admin
            name = f"@{username}" if username else first_name
            message += f"• {name}\n"
        
        return message
    
    @staticmethod
    def invite_message(username=None, first_name=None):
        if username:
            return f"🔔 @{username}, 3 روژە تە نە ئاخفتنی د گروپی دا نامەکێ ڤرێکە! 🗣️"
        else:
            return f"🔔 {first_name}, 3 روژە ئاکتیڤ نینی ئاکتیڤ بە! 🗣️"
    
    @staticmethod
    def user_stats(name, level, title, xp, msg_count, next_xp, last_date):
        return (
            f"📊 **داتایێن {name}**\n\n"
            f"🏆 **Level:** {level} - {title}\n"
            f"✨ **XP:** {xp}\n"
            f"💬 **توتالێ ناما:** {msg_count}\n"
            f"📈 **بۆ لیفلەکێ نڤ:** {next_xp} پوینت پێدفینە\n"
            f"⏰ **دوماهیک نامە:** {last_date[:10] if last_date else 'N/A'}"
        )
    
    @staticmethod
    def bot_start_message():
        return "🔰 سوپاس ئەز بوتێ داتایێن گروپی مە. بۆ هاریکاریێ دشێی چێکی /help"
    
    @staticmethod
    def bot_ready():
        return "✅ بوت ب سەرکەڤتیانە کارکر"


def get_iraq_time():
    tz = pytz.timezone('Asia/Baghdad')
    return datetime.datetime.now(tz)

def is_admin(bot, chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        return user_id in admin_ids
    except:
        return False

def get_user_display_name(user):
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"
        return full_name
    return "نەناسراب"
