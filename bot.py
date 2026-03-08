# bot.py - ANA DOSYA (GÜNCEL - NORMAL KULLANICILARA ETİKET ÖZELLİKLİ)
import telebot
import os
import time
import traceback
import requests
from telebot import types
from telebot.apihelper import ApiTelegramException

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

def set_user_title(chat_id, user_id, title):
    """Doğrudan Telegram API ile kullanıcı etiketi değiştir"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatMemberTitle"
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "custom_title": title[:16]  # Telegram 16 karakter sınırı
        }
        
        response = requests.post(url, data=data)
        result = response.json()
        
        if result.get("ok"):
            return True, None
        else:
            error = result.get("description", "Bilinmeyen hata")
            return False, error
            
    except Exception as e:
        return False, str(e)

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
            
            # Sonraki level için gereken XP
            if level < 70:
                if level < 11:
                    next_xp = level * 100
                elif level < 16:
                    next_xp = 1000 + ((level - 10) * 200)
                elif level < 21:
                    next_xp = 2000 + ((level - 15) * 300)
                elif level < 26:
                    next_xp = 3500 + ((level - 20) * 400)
                elif level < 31:
                    next_xp = 5500 + ((level - 25) * 500)
                elif level < 36:
                    next_xp = 8000 + ((level - 30) * 800)
                elif level < 41:
                    next_xp = 12000 + ((level - 35) * 1200)
                elif level < 46:
                    next_xp = 18000 + ((level - 40) * 1800)
                elif level < 51:
                    next_xp = 27000 + ((level - 45) * 2500)
                elif level < 56:
                    next_xp = 39500 + ((level - 50) * 3500)
                elif level < 61:
                    next_xp = 57000 + ((level - 55) * 5000)
                elif level < 66:
                    next_xp = 82000 + ((level - 60) * 7000)
                else:
                    next_xp = 117000 + ((level - 65) * 10000)
                
                xp_needed = next_xp - xp
                messages_needed = (xp_needed + 9) // 10
            else:
                messages_needed = 0
            
            msg = f"📊 **LEVEL BİLGİLERİN**\n\n"
            msg += f"🏆 **Level:** {level} - {title}\n"
            msg += f"✨ **XP:** {xp}\n"
            msg += f"💬 **نامه:** {msg_count}\n"
            
            if level < 70:
                msg += f"📈 **بۆ لیفلەکێ نڤ:** {messages_needed} mesaj\n"
            
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

# === TEST KOMUTU - Normal kullanıcıya etiket ekleme testi ===
@bot.message_handler(commands=['testtag'])
def cmd_testtag(message):
    """TEST: Normal kullanıcıya etiket ekle"""
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, "🚫 Bu komut sadece grupta çalışır")
            return
        
        user = message.from_user
        new_tag = "🔧 TEST TAG"
        
        # Doğrudan Telegram API'yi çağır
        success, error = set_user_title(message.chat.id, user.id, new_tag)
        
        if success:
            bot.reply_to(message, f"✅ Etiketin '{new_tag}' olarak değiştirildi! (Admin olmadın)")
        else:
            if "not enough rights" in error:
                bot.reply_to(message, "❌ Bot yetkisi yok! Lütfen botu grupta admin yap ve 'Üye Etiketlerini Düzenle' yetkisini ver.")
            else:
                bot.reply_to(message, f"❌ Hata: {error}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Hata: {e}")

# === MESAJ İŞLEYİCİ ===
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    try:
        if not is_allowed_group(message):
            return
        
        # Komutları tekrar kontrol et (handler sırası karışırsa diye)
        if message.text and message.text.startswith('/'):
            command = message.text.split()[0].lower()
            if command == '/level':
                cmd_level(message)
                return
            elif command == '/stats':
                cmd_stats(message)
                return
            elif command == '/top':
                cmd_top(message)
                return
            elif command == '/24h':
                cmd_24h(message)
                return
            elif command == '/nadmin':
                cmd_nadmin(message)
                return
            elif command == '/testid':
                cmd_testid(message)
                return
            elif command == '/testtag':
                cmd_testtag(message)
                return
            elif command == '/help':
                cmd_help(message)
                return
            elif command == '/start':
                cmd_start(message)
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
                
                # Premium emoji için HTML parse_mode ile gönder
                bot.send_message(
                    message.chat.id,
                    level_msg,
                    parse_mode='HTML'
                )
                
                # === YENİ: Normal kullanıcının etiketini değiştir ===
                try:
                    # Yeni level'a göre etiketi al
                    new_tag = level_system.get_level_tag(new_level)
                    
                    # Doğrudan Telegram API ile etiket değiştir
                    success, error = set_user_title(message.chat.id, user.id, new_tag)
                    
                    if success:
                        print(f"✅ {name} etiketi '{new_tag}' olarak değiştirildi")
                        # İsteğe bağlı: Başarılı mesajı gönder
                        # bot.send_message(message.chat.id, f"🏆 {name} artık **{new_tag}** oldu!")
                    else:
                        if "not enough rights" in error:
                            print(f"⚠️ Bot yetkisi yok: 'Üye Etiketlerini Düzenle' yetkisini kontrol et")
                        else:
                            print(f"❌ Etiket değiştirme hatası: {error}")
                            
                except Exception as e:
                    print(f"❌ Etiket değiştirme hatası: {e}")
                
                print(f"🎉 LEVEL UP! {name} -> Level {new_level}")
            
    except Exception as e:
        print(f"❌ handle_messages hatası: {e}")
        traceback.print_exc()

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
    print("   • /testtag (normal kullanıcı etiket testi)")
    print("-" * 50)
    print("🚀 Polling başlıyor...")
    print("=" * 50)
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Polling hatası: {e}")
        time.sleep(5)
