# bot.py
import telebot
import os
import time
import threading
from telebot import types

from config import BOT_TOKEN, ALLOWED_GROUP_ID
from database import Database
from levels import LevelSystem
from reports import ReportSystem
from utils import BadiniTranslations, is_admin, get_user_display_name

# Bot'u başlat
bot = telebot.TeleBot(BOT_TOKEN)
db = Database()
level_system = LevelSystem()
translations = BadiniTranslations()

# Rapor sistemini başlat
report_system = ReportSystem(bot, db, ALLOWED_GROUP_ID)

# Admin cache
admin_cache = set()

def update_admin_cache(chat_id):
    global admin_cache
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_cache = set([admin.user.id for admin in admins])
        
        for admin_id in admin_cache:
            db.update_admin_status(admin_id, True)
    except Exception as e:
        print(f"Admin cache güncelleme hatası: {e}")

def is_allowed_group(message):
    chat_id = message.chat.id
    
    # Private chat kontrolü - özelde asla çalışma
    if message.chat.type == 'private':
        return False
    
    return chat_id == ALLOWED_GROUP_ID

def is_user_admin(message):
    user_id = message.from_user.id
    return user_id in admin_cache

# === MESAJ İŞLEYİCİ ===
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'sticker', 'voice'])
def handle_all_messages(message):
    # Özel mesajları engelle
    if message.chat.type == 'private':
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if not is_allowed_group(message):
        return
    
    chat_id = message.chat.id
    user = message.from_user
    
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    leveled_up, new_level, title = db.update_user_activity(user.id)
    
    if leveled_up:
        user_name = get_user_display_name(user)
        level_msg = translations.level_up_message(user.username or user.first_name, new_level, title)
        
        bot.send_message(chat_id, level_msg, parse_mode='Markdown')

# === KOMUTLAR ===
@bot.message_handler(commands=['start'])
def cmd_start(message):
    if message.chat.type == 'private':
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if not is_allowed_group(message):
        return
    
    bot.reply_to(message, translations.bot_start_message(), parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def cmd_help(message):
    if message.chat.type == 'private':
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if not is_allowed_group(message):
        return
    
    help_text = "**فرمانێن بوت:**\n\n"
    for cmd, desc in translations.command_descriptions().items():
        help_text += f"{desc}\n"
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['level', 'stats'])
def cmd_level(message):
    if message.chat.type == 'private':
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if not is_allowed_group(message):
        return
    
    user_id = message.from_user.id
    stats = db.get_user_stats(user_id)
    
    if stats:
        username, first_name, xp, level, msg_count, last_date = stats
        name = f"@{username}" if username else first_name
        title = level_system.get_level_title(level)
        
        next_level_xp = (level * 100)
        next_xp_needed = next_level_xp - xp
        
        stats_msg = translations.user_stats(name, level, title, xp, msg_count, next_xp_needed, last_date)
        bot.reply_to(message, stats_msg, parse_mode='Markdown')
    else:
        bot.reply_to(message, translations.error_message("no_user"))

@bot.message_handler(commands=['top'])
def cmd_top(message):
    if message.chat.type == 'private':
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if not is_allowed_group(message):
        return
    
    top_users = db.get_top_users(10)
    top_msg = level_system.format_top_list(top_users)
    bot.reply_to(message, top_msg, parse_mode='Markdown')

@bot.message_handler(commands=['24h'])
def cmd_24h(message):
    if message.chat.type == 'private':
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if not is_allowed_group(message):
        return
    
    if not is_user_admin(message):
        bot.reply_to(message, translations.error_message("not_admin"))
        return
    
    inactive_users = db.get_inactive_users_24h()
    report = translations.inactive_24h_report(inactive_users, len(inactive_users))
    bot.reply_to(message, report, parse_mode='Markdown')

@bot.message_handler(commands=['nadmin'])
def cmd_nadmin(message):
    if message.chat.type == 'private':
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if not is_allowed_group(message):
        return
    
    if not is_user_admin(message):
        bot.reply_to(message, translations.error_message("not_admin"))
        return
    
    chat_id = message.chat.id
    bot.reply_to(message, "🔄 ڕێڤەبەر تێنە کنترولکرن...", parse_mode='Markdown')
    
    try:
        admins = bot.get_chat_administrators(chat_id)
        current_admins = [admin.user.id for admin in admins]
        
        new_admins = []
        for admin_id in current_admins:
            if admin_id not in admin_cache:
                try:
                    user = bot.get_chat_member(chat_id, admin_id).user
                    db.add_user(admin_id, user.username, user.first_name, user.last_name)
                    db.update_admin_status(admin_id, True)
                    
                    user_info = (admin_id, user.username, user.first_name)
                    new_admins.append(user_info)
                except:
                    pass
        
        update_admin_cache(chat_id)
        
        result_msg = translations.new_admins_message(new_admins)
        bot.send_message(chat_id, result_msg, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ خەلەت: {str(e)}")

# === GRUP OLAYLARI ===
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    if message.chat.type == 'private':
        return
    
    if not is_allowed_group(message):
        return
    
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            bot.reply_to(message, translations.bot_start_message(), parse_mode='Markdown')
            update_admin_cache(message.chat.id)

# === ANA ÇALIŞTIRMA ===
if __name__ == "__main__":
    print("🤖 Badînî Bot tê başkirin...")
    print(f"🔑 Token: {BOT_TOKEN[:10]}...")
    print(f"👥 Gruba destûrdayî: {ALLOWED_GROUP_ID}")
    print(translations.bot_ready())
    
    try:
        update_admin_cache(ALLOWED_GROUP_ID)
    except:
        print("⚠️ Admin listesi alinamadi.")
    
    bot.infinity_polling()
