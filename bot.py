# bot.py - ANA DOSYA (VIP/SVIP SİSTEMLİ + id KOMUTLU)
import telebot
import os
import time
import re
from telebot import types

from config import BOT_TOKEN, ALLOWED_GROUP_ID
from database import Database
from levels import LevelSystem
from reports import ReportSystem
from utils import BadiniTranslations, get_user_display_name, get_mention_html

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
            mention = get_mention_html(user_id, username, first_name)
            title = level_system.get_level_title(level)
            
            # Sonraki level için gereken XP
            if level < 90:
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
                elif level < 71:
                    next_xp = 117000 + ((level - 65) * 10000)
                elif level < 81:
                    # VIP level (71-80) her biri 10000 XP
                    next_xp = 167000 + ((level - 70) * 10000)
                elif level < 91:
                    # SVIP level (81-90) her biri 10000 XP
                    next_xp = 267000 + ((level - 80) * 10000)
                else:
                    next_xp = 367000
                
                if level >= 90:
                    messages_needed = 0
                else:
                    xp_needed = next_xp - xp
                    messages_needed = (xp_needed + 9) // 10
            else:
                messages_needed = 0
            
            msg = f"📊 LEVEL BİLGİLERİN\n\n"
            msg += f"👤 Kullanıcı: {mention}\n"
            msg += f"🏆 Level: {level} - {title}\n"
            msg += f"✨ XP: {xp}\n"
            msg += f"💬 Mesaj: {msg_count}\n"
            
            if level < 90:
                msg += f"📈 Sonraki levele: {messages_needed} mesaj\n"
            else:
                msg += f"👑 MAX LEVEL! 👑\n"
            
            if last_date:
                msg += f"⏰ Son mesaj: {last_date[:10]}"
            
            bot.reply_to(message, msg, parse_mode='HTML')
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
            mention = get_mention_html(user_id, username, first_name)
            
            msg = f"📊 İSTATİSTİKLERİN\n\n"
            msg += f"👤 Kullanıcı: {mention}\n"
            msg += f"💬 Toplam Mesaj: {msg_count}\n"
            msg += f"🏆 Level: {level}\n"
            msg += f"✨ XP: {xp}\n"
            
            if last_date:
                msg += f"⏰ Son Mesaj: {last_date[:10]}"
            
            bot.reply_to(message, msg, parse_mode='HTML')
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
        
        if not top_users:
            bot.reply_to(message, "🏆 لیستا ڤاله‌یه - هێچ کاربەر نینە")
            return
        
        message_text = "🏆 لیستا ڕیزبه‌ندیان\n\n"
        
        for i, user in enumerate(top_users[:10], 1):
            user_id, username, first_name, xp, level, msg_count = user
            mention = get_mention_html(user_id, username, first_name)
            title = level_system.get_level_title(level)
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message_text += f"{medal} {mention}\n"
            message_text += f"   • Level {level} - {title}\n"
            message_text += f"   • XP: {xp} | Mesaj: {msg_count}\n\n"
        
        bot.reply_to(message, message_text, parse_mode='HTML')
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
        
        if not inactive_users:
            bot.reply_to(message, "📊 راپورا 24 سعەتان - هەمی ئاکتیڤن 🎉")
            return
        
        message_text = "لیستا وان کەسێن نامە ڤرێنەکرین د ماوێ 24 سعەتاندا\n\n"
        for user in inactive_users:
            user_id, username, first_name = user
            mention = get_mention_html(user_id, username, first_name)
            message_text += f"• {mention}\n"
        
        bot.reply_to(message, message_text, parse_mode='HTML')
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

# === İD KOMUTU (slashsiz) ===
@bot.message_handler(func=lambda message: message.text and message.text.lower() in ['id', 'ايدي', 'ایدی'])
def cmd_id(message):
    """Kullanıcı bilgilerini göster (profil fotoğraflı)"""
    try:
        if not is_allowed_group(message):
            return
        
        user = message.from_user
        user_id = user.id
        
        # Kullanıcıyı veritabanına ekle/güncelle
        db.add_user(user_id, user.username, user.first_name, user.last_name)
        
        # Kullanıcı istatistiklerini al
        stats = db.get_user_stats(user_id)
        
        if not stats:
            bot.reply_to(message, "📊 İstatistik bulunamadı")
            return
        
        username, first_name, xp, level, msg_count, last_date = stats
        title = level_system.get_level_title(level)
        
        # Kullanıcının dili (Telegram dil ayarı)
        user_lang = user.language_code or "bilinmiyor"
        
        # Gruba katılma tarihi
        db.cursor.execute('SELECT joined_date FROM users WHERE user_id = ?', (user_id,))
        joined_result = db.cursor.fetchone()
        joined_date = joined_result[0][:10] if joined_result and joined_result[0] else "bilinmiyor"
        
        # Kullanıcının bio'sunu al (varsa) - LİNKLER VE @'LER TAMAMEN SİLİNECEK
        bio = ""
        try:
            user_profile = bot.get_chat(user_id)
            if hasattr(user_profile, 'bio') and user_profile.bio:
                bio = user_profile.bio
                
                # Tüm linkleri ve @ işaretlerini TAMAMEN SİL
                # http, https linkleri sil
                bio = re.sub(r'https?://\S+', '', bio)
                # www linkleri sil
                bio = re.sub(r'www\.\S+', '', bio)
                # t.me linkleri sil
                bio = re.sub(r't\.me/\S+', '', bio)
                # telegram.me linkleri sil
                bio = re.sub(r'telegram\.me/\S+', '', bio)
                # telegram.org linkleri sil
                bio = re.sub(r'telegram\.org/\S+', '', bio)
                # telegram.dog linkleri sil
                bio = re.sub(r'telegram\.dog/\S+', '', bio)
                # @ ile başlayan her şeyi sil
                bio = re.sub(r'@\S+', '', bio)
                
                # Birden fazla boşluk varsa teke indir
                bio = re.sub(r'\s+', ' ', bio)
                
                # Baştaki ve sondaki boşlukları temizle
                bio = bio.strip()
                
                # Eğer bio tamamen boşaldıysa
                if not bio:
                    bio = "🚫 Bio yok"
            else:
                bio = "🚫 Bio yok"
        except Exception as e:
            print(f"❌ Bio alınamadı: {e}")
            bio = "🚫 Bio alınamadı"
        
        # Görünen ad için tıklanabilir link hazırla (username'siz)
        name_mention = f"<a href='tg://user?id={user_id}'>{first_name if first_name else 'İsimsiz'}</a>"
        
        # Kullanıcı adı (varsa @'li, yoksa ❌)
        user_text = f"@{username}" if username else "❌"
        
        # Mesajı oluştur
        caption = f"𖤓 𝐧𝐚𝐦𝐞 {name_mention}\n"
        caption += f"𖤓 𝐮𝐬𝐞𝐫 {user_text}\n"
        caption += f"𖤓 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 {msg_count}\n"
        caption += f"𖤓 𝐥𝐞𝐧𝐠 {user_lang}\n"
        caption += f"𖤓 𝐭𝐢𝐦𝐞 {joined_date}\n"
        caption += f"𖤓 𝐥𝐞𝐯𝐞𝐥 {level} - {title}\n"
        caption += f"𖤓 𝐢𝐝 <code>{user_id}</code>\n"
        caption += f"𖤓 𝐛𝐢𝐨 {bio}"
        
        # Profil fotoğrafını al ve gönder
        try:
            photos = bot.get_user_profile_photos(user_id, limit=1)
            
            if photos and photos.total_count > 0:
                # Profil fotoğrafı var
                file_id = photos.photos[0][-1].file_id  # En büyük boy
                bot.send_photo(
                    message.chat.id,
                    file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            else:
                # Profil fotoğrafı yok
                bot.send_message(
                    message.chat.id,
                    caption,
                    parse_mode='HTML'
                )
        except:
            # Fotoğraf alınamadı
            bot.send_message(
                message.chat.id,
                caption,
                parse_mode='HTML'
            )
        
    except Exception as e:
        print(f"❌ id komutu hatası: {e}")
        bot.reply_to(message, "❌ Bir hata oluştu")

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
            elif command == '/help':
                cmd_help(message)
                return
            elif command == '/start':
                cmd_start(message)
                return
        
        # Normal mesaj - XP ekle ve isim güncelle
        user = message.from_user
        db.add_user(user.id, user.username, user.first_name, user.last_name)
        
        leveled_up, new_level = db.update_user_activity(user.id)
        
        if leveled_up:
            # Kullanıcının güncel XP'sini al
            stats = db.get_user_stats(user.id)
            if stats:
                username, first_name, xp, level, msg_count, last_date = stats
                
                # Tıklanabilir mention oluştur
                mention = get_mention_html(user.id, username, first_name)
                
                # YENİ FORMAT ile level atlama mesajı (tıklanabilir isimli)
                level_msg = level_system.format_level_message(mention, new_level, xp)
                
                # Premium emoji için HTML parse_mode ile gönder
                bot.send_message(
                    message.chat.id,
                    level_msg,
                    parse_mode='HTML'
                )
                print(f"🎉 LEVEL UP! {mention} -> Level {new_level}")
            
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
    print("   • id, ايدي, ایدی (slashsiz)")
    print("-" * 50)
    print("🚀 Polling başlıyor...")
    print("=" * 50)
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Polling hatası: {e}")
        time.sleep(5)
