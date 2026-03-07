# bot.py - TAM DOSYA (GÜNCELLENMİŞ)
import telebot
import os
import time
from telebot import types

from config import BOT_TOKEN, ALLOWED_GROUP_ID
from database import Database
from levels import LevelSystem
from reports import ReportSystem
from utils import BadiniTranslations, get_user_display_name

# Bot'u başlat
bot = telebot.TeleBot(BOT_TOKEN)
db = Database()
level_system = LevelSystem()
translations = BadiniTranslations()

# Admin cache
admin_cache = set()

# Rapor sistemini başlat
report_system = ReportSystem(bot, db, ALLOWED_GROUP_ID)

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

# === KOMUTLAR ===
@bot.message_handler(commands=['start'])
def cmd_start(message):
    print(f"📌 /start - User: {message.from_user.id}")
    try:
        if message.chat.type == 'private':
            bot.reply_to(message, "🚫 Bot sadece grupta çalışır")
            return
        
        bot.reply_to(message, translations.bot_start_message())
    except Exception as e:
        print(f"❌ start hatası: {e}")

@bot.message_handler(commands=['help'])
def cmd_help(message):
    print(f"📌 /help")
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, translations.error_message("wrong_group"))
            return
        
        help_text = "📋 فرمانێن بوت:\n\n"
        for cmd, desc in translations.command_descriptions().items():
            help_text += f"{desc}\n"
        
        bot.reply_to(message, help_text)
    except Exception as e:
        print(f"❌ help hatası: {e}")

@bot.message_handler(commands=['level'])
def cmd_level(message):
    print(f"📌 /level")
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, translations.error_message("wrong_group"))
            return
        
        user_id = message.from_user.id
        stats = db.get_user_stats(user_id)
        
        if not stats:
            user = message.from_user
            db.add_user(user_id, user.username, user.first_name, user.last_name)
            stats = db.get_user_stats(user_id)
        
        if stats:
            username, first_name, xp, level, msg_count, last_date = stats
            name = f"@{username}" if username else first_name
            title = level_system.get_level_title(level)
            
            next_level_xp = (level * 100)
            xp_needed = next_level_xp - xp
            
            msg = f"📊 **LEVEL BİLGİLERİN**\n\n"
            msg += f"🏆 **Level:** {level} - {title}\n"
            msg += f"✨ **XP:** {xp}\n"
            msg += f"💬 **نامه:** {msg_count}\n"
            
            if level < 70:
                msg += f"📈 **بۆ لیفلەکێ نڤ:** {xp_needed} XP\n"
            
            if last_date:
                msg += f"⏰ **دوماهیک نامە:** {last_date[:10]}"
            
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, translations.error_message("no_user"))
    except Exception as e:
        print(f"❌ level hatası: {e}")
        bot.reply_to(message, translations.error_message("general"))

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    print(f"📌 /stats")
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, translations.error_message("wrong_group"))
            return
        
        user_id = message.from_user.id
        stats = db.get_user_stats(user_id)
        
        if not stats:
            user = message.from_user
            db.add_user(user_id, user.username, user.first_name, user.last_name)
            stats = db.get_user_stats(user_id)
        
        if stats:
            username, first_name, xp, level, msg_count, last_date = stats
            name = f"@{username}" if username else first_name
            
            msg = f"📊 **İSTATİSTİKLERİN**\n\n"
            msg += f"👤 **İsim:** {name}\n"
            msg += f"💬 **Toplam Mesaj:** {msg_count}\n"
            msg += f"🏆 **Level:** {level}\n"
            msg += f"✨ **XP:** {xp}\n"
            
            if last_date:
                msg += f"⏰ **Son Mesaj:** {last_date[:10]}"
            
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, translations.error_message("no_user"))
    except Exception as e:
        print(f"❌ stats hatası: {e}")
        bot.reply_to(message, translations.error_message("general"))

@bot.message_handler(commands=['top'])
def cmd_top(message):
    print(f"📌 /top")
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, translations.error_message("wrong_group"))
            return
        
        top_users = db.get_top_users(10)
        top_msg = level_system.format_top_list(top_users)
        bot.reply_to(message, top_msg)
    except Exception as e:
        print(f"❌ top hatası: {e}")
        bot.reply_to(message, translations.error_message("general"))

@bot.message_handler(commands=['24h'])
def cmd_24h(message):
    print(f"📌 /24h")
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, translations.error_message("wrong_group"))
            return
        
        if message.from_user.id not in admin_cache:
            bot.reply_to(message, translations.error_message("not_admin"))
            return
        
        inactive_users = db.get_inactive_users_24h()
        report = translations.inactive_24h_report(inactive_users)
        bot.reply_to(message, report)
    except Exception as e:
        print(f"❌ 24h hatası: {e}")
        bot.reply_to(message, translations.error_message("general"))

@bot.message_handler(commands=['nadmin'])
def cmd_nadmin(message):
    print(f"📌 /nadmin")
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, translations.error_message("wrong_group"))
            return
        
        if message.from_user.id not in admin_cache:
            bot.reply_to(message, translations.error_message("not_admin"))
            return
        
        update_admin_cache(message.chat.id)
        bot.reply_to(message, f"👑 ڕێڤەبەر هاتنە دیتن: {len(admin_cache)} کەس")
    except Exception as e:
        print(f"❌ nadmin hatası: {e}")
        bot.reply_to(message, translations.error_message("general"))

@bot.message_handler(commands=['testid'])
def cmd_testid(message):
    print(f"📌 /testid")
    try:
        if message.chat.type == 'private':
            bot.reply_to(message, "🚫 Bu özel sohbet")
            return
        
        is_admin = message.from_user.id in admin_cache
        
        msg = (
            f"📊 GRUP BİLGİLERİ\n\n"
            f"🆔 Grup ID: {message.chat.id}\n"
            f"🔑 İzin verilen: {ALLOWED_GROUP_ID}\n"
            f"✅ Eşleşiyor: {'✅' if message.chat.id == ALLOWED_GROUP_ID else '❌'}\n"
            f"👤 Sizin ID: {message.from_user.id}\n"
            f"👑 Admin: {'✅' if is_admin else '❌'}\n"
            f"📊 Toplam admin: {len(admin_cache)}"
        )
        bot.reply_to(message, msg)
    except Exception as e:
        print(f"❌ testid hatası: {e}")
        bot.reply_to(message, f"❌ Hata: {e}")

# === MESAJ İŞLEYİCİ ===
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    try:
        if not is_allowed_group(message):
            return
        
        # Normal mesaj - XP ekle
        user = message.from_user
        db.add_user(user.id, user.username, user.first_name, user.last_name)
        
        leveled_up, new_level = db.update_user_activity(user.id)
        
        if leveled_up:
            name = get_user_display_name(user)
            
            # Kullanıcının güncel XP'sini al
            stats = db.get_user_stats(user.id)
            if stats:
                username, first_name, xp, level, msg_count, last_date = stats
                
                # YENİ FORMAT ile level atlama mesajı
                level_msg, emoji = level_system.format_level_message(name, new_level, xp)
                
                # Premium emoji için HTML parse_mode kullan
                bot.send_message(
                    message.chat.id,
                    level_msg,
                    parse_mode='HTML'
                )
                print(f"🎉 Level up: {name} -> {new_level}")
            
    except Exception as e:
        print(f"❌ handle_messages hatası: {e}")

# === GRUP OLAYLARI ===
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    try:
        if not is_allowed_group(message):
            return
        
        for new_member in message.new_chat_members:
            if new_member.id == bot.get_me().id:
                bot.reply_to(message, translations.bot_start_message())
                update_admin_cache(message.chat.id)
                print("✅ Bot gruba eklendi!")
            else:
                db.add_user(new_member.id, new_member.username, new_member.first_name, new_member.last_name)
                print(f"✅ Yeni üye: {new_member.first_name}")
    except Exception as e:
        print(f"❌ new_member hatası: {e}")

# === ANA ÇALIŞTIRMA ===
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 BADÎNÎ BOT BAŞLATILIYOR...")
    print("=" * 50)
    print(f"🔑 Token: {BOT_TOKEN[:10]}...")
    print(f"👥 Grup ID: {ALLOWED_GROUP_ID}")
    print("-" * 50)
    
    # Admin cache'i güncelle
    try:
        update_admin_cache(ALLOWED_GROUP_ID)
    except Exception as e:
        print(f"⚠️ Admin cache alınamadı: {e}")
    
    print("-" * 50)
    print("✅ HAZIR KOMUTLAR:")
    print("   • /start, /help")
    print("   • /level, /stats")
    print("   • /top")
    print("   • /24h (admin)")
    print("   • /nadmin (admin)")
    print("   • /testid")
    print("-" * 50)
    print("🚀 Polling başlıyor...")
    print("=" * 50)
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Polling hatası: {e}")
        time.sleep(5)
