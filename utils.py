# utils.py
import datetime
import pytz
from config import IRAQ_TIMEZONE

class BadiniTranslations:
    @staticmethod
    def bot_start_message():
        return "🔰 سوپاس ئەز بوتێ داتایێن گروپی مە. بۆ هاریکاریێ دشێی چێکی /help"
    
    @staticmethod
    def error_message(error_type="general"):
        errors = {
            "wrong_group": "🚫 ئەڤ بوتە تنێ د گروپێ تایبەت دا کار دکەت",
            "not_admin": "⛔ تنێ ئادمین دشێن ڤی بەشی بکار بینن",
            "general": "❌ خەلەتیەک چێبی دوبارە هەول بدە",
            "no_user": "👤 ئەڤ کەسە نەهاتە دیتن"
        }
        return errors.get(error_type, errors["general"])
    
    @staticmethod
    def command_descriptions():
        return {
            "start": "🔰 /start - بوت دەست پێ بکە",
            "help": "❓ /help - هەمی فرمانان نیشان بدە",
            "level": "📊 /level - لیفلێ خۆ نیشان بدە",
            "stats": "📈 /stats - داتایێن خۆ نیشان بدە",
            "top": "🏆 /top - ئەندامێن لیفل بلند",
            "24h": "⏰ /24h - کەسێن 24 سەعتاندا نە ئاخفتین (ئادمین)",
            "nadmin": "👑 /nadmin - ڕێڤەبەرێن نوی ببینە (ئادمین)"
        }
    
    @staticmethod
    def inactive_24h_report(inactive_list):
        if not inactive_list:
            return "📊 راپورا 24 سعەتان - هەمی ئاکتیڤن 🎉"
        
        message = "لیستا وان کەسێن نامە ڤرێنەکرین د ماوێ 24 سعەتاندا\n\n"
        for user in inactive_list:
            user_id, username, first_name = user
            name = f"@{username}" if username else first_name
            message += f"• {name}\n"
        
        return message
    
    @staticmethod
    def new_admins_message(new_admins):
        if not new_admins:
            return "👑 ڕێڤەبەرێن نوی نەهاتنە دیتن"
        
        message = "👑 ڕێڤەبەرێن نوی هاتنە دیتن:\n\n"
        for admin in new_admins:
            user_id, username, first_name = admin
            name = f"@{username}" if username else first_name
            message += f"• {name}\n"
        
        return message

def get_iraq_time():
    tz = pytz.timezone('Asia/Baghdad')
    return datetime.datetime.now(tz)

def get_user_display_name(user):
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    return "کاربەر"

def truncate_tag(tag, max_length=16):
    """Etiket çok uzunsa kısalt"""
    if len(tag) > max_length:
        return tag[:max_length-3] + "..."
    return tag
