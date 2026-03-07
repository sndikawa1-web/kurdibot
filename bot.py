# bot.py - DÜZELTİLMİŞ VERSİYON
import telebot
import os
import time
from telebot import types

# Token ve grup ID
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
ALLOWED_GROUP_ID = int(os.environ.get('GROUP_ID', '0'))

# Bot'u başlat
bot = telebot.TeleBot(BOT_TOKEN)

# Admin cache
admin_cache = set()

# === YARDIMCI FONKSİYONLAR ===
def update_admin_cache(chat_id):
    global admin_cache
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_cache = set([admin.user.id for admin in admins])
        print(f"✅ Admin cache: {len(admin_cache)} admin")
    except Exception as e:
        print(f"❌ Admin cache hatası: {e}")

def is_allowed_group(message):
    if message.chat.type == 'private':
        return False
    return message.chat.id == ALLOWED_GROUP_ID

# === BADÎNÎ ÇEVİRİLER ===
class BadiniTranslations:
    @staticmethod
    def bot_start_message():
        return "🔰 سوپاس ئەز بوتێ داتایێن گروپی مە. بۆ هاریکاریێ دشێی چێکی /help"
    
    @staticmethod
    def error_message(error_type="general"):
        errors = {
            "wrong_group": "🚫 ئەڤ بوتە تنێ د گروپێ تایبەت دا کار دکەت",
            "not_admin": "⛔ تنێ ئادمین دشێن ڤی بەشی بکار بینن",
            "general": "❌ خەلەتیەک چێبی"
        }
        return errors.get(error_type, errors["general"])
    
    @staticmethod
    def command_descriptions():
        return {
            "start": "🔰 /start - بوت دەست پێ بکە",
            "help": "❓ /help - هەمی فرمانان نیشان بدە",
            "level": "📊 /level - لیفلێ خۆ نیشان بدە",
            "stats": "📈 /stats - داتایێن خۆ نیشان بدە",
            "top": "🏆 /top - ئەندامێن بیلیفتا هەرێ بلند",
            "24h": "⏰ /24h - کەسێن 24 سەعتاندا نە ئاخفتین (ئادمین)",
            "nadmin": "👑 /nadmin - ڕێڤەبەرێن نوی ببینە (ئادمین)"
        }

translations = BadiniTranslations()

# === ÖNCE TÜM KOMUTLAR ===
@bot.message_handler(commands=['start'])
def cmd_start(message):
    print(f"/start komutu alındı: {message.from_user.id}")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    bot.reply_to(message, translations.bot_start_message(), parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def cmd_help(message):
    print(f"/help komutu alındı")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    help_text = "**📋 فرمانێن بوت:**\n\n"
    for cmd, desc in translations.command_descriptions().items():
        help_text += f"{desc}\n"
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['level', 'stats'])
def cmd_level(message):
    print(f"/level komutu alındı")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    user = message.from_user
    name = f"@{user.username}" if user.username else user.first_name
    
    # Basit level bilgisi (gerçek DB olmadan)
    msg = (
        f"📊 **داتایێن {name}**\n\n"
        f"🏆 **Level:** 1\n"
        f"✨ **XP:** 0\n"
        f"💬 **نامه:** 0"
    )
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['top'])
def cmd_top(message):
    print(f"/top komutu alındı")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    msg = "🏆 **لیستا ڕیزبه‌ندیان**\n\n"
    msg += "1. Test User - Level 1"
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['24h'])
def cmd_24h(message):
    print(f"/24h komutu alındı")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    # Admin kontrolü
    if message.from_user.id not in admin_cache:
        bot.reply_to(message, translations.error_message("not_admin"))
        return
    
    bot.reply_to(message, "📊 راپورا 24 سعەتان - هەمی ئاکتیڤن 🎉")

@bot.message_handler(commands=['nadmin'])
def cmd_nadmin(message):
    print(f"/nadmin komutu alındı")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if message.from_user.id not in admin_cache:
        bot.reply_to(message, translations.error_message("not_admin"))
        return
    
    update_admin_cache(message.chat.id)
    bot.reply_to(message, f"👑 ڕێڤەبەر هاتنە دیتن: {len(admin_cache)} کەس")

@bot.message_handler(commands=['testid'])
def cmd_testid(message):
    print(f"/testid komutu alındı")
    if message.chat.type == 'private':
        bot.reply_to(message, "Bu özel sohbet")
        return
    
    msg = (
        f"📊 **GRUP BİLGİLERİ**\n\n"
        f"🆔 Grup ID: `{message.chat.id}`\n"
        f"🔑 İzin verilen: `{ALLOWED_GROUP_ID}`\n"
        f"✅ Eşleşiyor: {'EVET' if message.chat.id == ALLOWED_GROUP_ID else 'HAYIR'}\n"
        f"👤 Sizin ID: {message.from_user.id}\n"
        f"👑 Admin misiniz: {'EVET' if message.from_user.id in admin_cache else 'HAYIR'}"
    )
    bot.reply_to(message, msg, parse_mode='Markdown')

# === SON OLARAK DİĞER MESAJLAR ===
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    print(f"Normal mesaj: {message.text}")
    if not is_allowed_group(message):
        return
    # Normal mesajlara yanıt verme, sadece logla
    pass

# === GRUP OLAYLARI ===
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    if not is_allowed_group(message):
        return
    
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            bot.reply_to(message, translations.bot_start_message())
            update_admin_cache(message.chat.id)
            print("✅ Bot gruba eklendi!")

# === ANA ÇALIŞTIRMA ===
if __name__ == "__main__":
    print("🤖 BOT BAŞLATILIYOR...")
    print(f"Token: {BOT_TOKEN[:10]}...")
    print(f"Grup ID: {ALLOWED_GROUP_ID}")
    
    # Admin cache'i güncelle
    try:
        update_admin_cache(ALLOWED_GROUP_ID)
    except:
        print("⚠️ Admin cache alınamadı")
    
    print("🚀 Polling başlıyor...")
    bot.infinity_polling()
