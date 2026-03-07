# bot.py - BADÎNÎ BOT PREMIUM EMOJİLİ SON VERSİYON
import telebot
import os
import sqlite3
import datetime
import time
from telebot import types

# === KONFİGÜRASYON ===
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
ALLOWED_GROUP_ID = int(os.environ.get('GROUP_ID', '0'))
DB_NAME = "badini_bot.db"
XP_PER_MESSAGE = 10

# Bot'u başlat
bot = telebot.TeleBot(BOT_TOKEN)
admin_cache = set()

# === PREMIUM EMOJİ KONFİGÜRASYONU ===
# Buraya Telegram premium emoji ID'lerini girin
EMOJI_CONFIG = {
    # Diamond level 1-10
    1: {"emoji_id": "5367422806881622129", "title": "Diamond 💎"},
    2: {"emoji_id": "5367422806881622130", "title": "Diamond 💎"},
    3: {"emoji_id": "5367422806881622131", "title": "Diamond 💎"},
    4: {"emoji_id": "5367422806881622132", "title": "Diamond 💎"},
    5: {"emoji_id": "5367422806881622133", "title": "Diamond 💎"},
    6: {"emoji_id": "5367422806881622134", "title": "Diamond 💎"},
    7: {"emoji_id": "5367422806881622135", "title": "Diamond 💎"},
    8: {"emoji_id": "5367422806881622136", "title": "Diamond 💎"},
    9: {"emoji_id": "5367422806881622137", "title": "Diamond 💎"},
    10: {"emoji_id": "5367422806881622138", "title": "Diamond 💎"},
    
    # Pro level 11-19
    11: {"emoji_id": "5367422806881622139", "title": "Pro ⚡"},
    12: {"emoji_id": "5367422806881622140", "title": "Pro ⚡"},
    13: {"emoji_id": "5367422806881622141", "title": "Pro ⚡"},
    14: {"emoji_id": "5367422806881622142", "title": "Pro ⚡"},
    15: {"emoji_id": "5367422806881622143", "title": "Pro ⚡"},
    16: {"emoji_id": "5367422806881622144", "title": "Pro ⚡"},
    17: {"emoji_id": "5367422806881622145", "title": "Pro ⚡"},
    18: {"emoji_id": "5367422806881622146", "title": "Pro ⚡"},
    19: {"emoji_id": "5367422806881622147", "title": "Pro ⚡"},
    
    # Pro Leader level 20-29 (iki emoji yan yana)
    20: {"emoji_id": ["5367422806881622148", "5367422806881622149"], "title": "Pro Leader 👑⚡"},
    21: {"emoji_id": ["5367422806881622150", "5367422806881622151"], "title": "Pro Leader 👑⚡"},
    22: {"emoji_id": ["5367422806881622152", "5367422806881622153"], "title": "Pro Leader 👑⚡"},
    23: {"emoji_id": ["5367422806881622154", "5367422806881622155"], "title": "Pro Leader 👑⚡"},
    24: {"emoji_id": ["5367422806881622156", "5367422806881622157"], "title": "Pro Leader 👑⚡"},
    25: {"emoji_id": ["5367422806881622158", "5367422806881622159"], "title": "Pro Leader 👑⚡"},
    26: {"emoji_id": ["5367422806881622160", "5367422806881622161"], "title": "Pro Leader 👑⚡"},
    27: {"emoji_id": ["5367422806881622162", "5367422806881622163"], "title": "Pro Leader 👑⚡"},
    28: {"emoji_id": ["5367422806881622164", "5367422806881622165"], "title": "Pro Leader 👑⚡"},
    29: {"emoji_id": ["5367422806881622166", "5367422806881622167"], "title": "Pro Leader 👑⚡"},
    
    # King level 30-39
    30: {"emoji_id": "5367422806881622168", "title": "King 👑"},
    31: {"emoji_id": "5367422806881622169", "title": "King 👑"},
    32: {"emoji_id": "5367422806881622170", "title": "King 👑"},
    33: {"emoji_id": "5367422806881622171", "title": "King 👑"},
    34: {"emoji_id": "5367422806881622172", "title": "King 👑"},
    35: {"emoji_id": "5367422806881622173", "title": "King 👑"},
    36: {"emoji_id": "5367422806881622174", "title": "King 👑"},
    37: {"emoji_id": "5367422806881622175", "title": "King 👑"},
    38: {"emoji_id": "5367422806881622176", "title": "King 👑"},
    39: {"emoji_id": "5367422806881622177", "title": "King 👑"},
    
    # Dragon level 40-49
    40: {"emoji_id": "5367422806881622178", "title": "Dragon 🐉"},
    41: {"emoji_id": "5367422806881622179", "title": "Dragon 🐉"},
    42: {"emoji_id": "5367422806881622180", "title": "Dragon 🐉"},
    43: {"emoji_id": "5367422806881622181", "title": "Dragon 🐉"},
    44: {"emoji_id": "5367422806881622182", "title": "Dragon 🐉"},
    45: {"emoji_id": "5367422806881622183", "title": "Dragon 🐉"},
    46: {"emoji_id": "5367422806881622184", "title": "Dragon 🐉"},
    47: {"emoji_id": "5367422806881622185", "title": "Dragon 🐉"},
    48: {"emoji_id": "5367422806881622186", "title": "Dragon 🐉"},
    49: {"emoji_id": "5367422806881622187", "title": "Dragon 🐉"},
    
    # Myth level 50-59 (iki emoji yan yana)
    50: {"emoji_id": ["5367422806881622188", "5367422806881622189"], "title": "Myth 🔱✨"},
    51: {"emoji_id": ["5367422806881622190", "5367422806881622191"], "title": "Myth 🔱✨"},
    52: {"emoji_id": ["5367422806881622192", "5367422806881622193"], "title": "Myth 🔱✨"},
    53: {"emoji_id": ["5367422806881622194", "5367422806881622195"], "title": "Myth 🔱✨"},
    54: {"emoji_id": ["5367422806881622196", "5367422806881622197"], "title": "Myth 🔱✨"},
    55: {"emoji_id": ["5367422806881622198", "5367422806881622199"], "title": "Myth 🔱✨"},
    56: {"emoji_id": ["5367422806881622200", "5367422806881622201"], "title": "Myth 🔱✨"},
    57: {"emoji_id": ["5367422806881622202", "5367422806881622203"], "title": "Myth 🔱✨"},
    58: {"emoji_id": ["5367422806881622204", "5367422806881622205"], "title": "Myth 🔱✨"},
    59: {"emoji_id": ["5367422806881622206", "5367422806881622207"], "title": "Myth 🔱✨"},
    
    # King Dragon level 60-70
    60: {"emoji_id": "5367422806881622208", "title": "King Dragon 👑🐉"},
    61: {"emoji_id": "5367422806881622209", "title": "King Dragon 👑🐉"},
    62: {"emoji_id": "5367422806881622210", "title": "King Dragon 👑🐉"},
    63: {"emoji_id": "5367422806881622211", "title": "King Dragon 👑🐉"},
    64: {"emoji_id": "5367422806881622212", "title": "King Dragon 👑🐉"},
    65: {"emoji_id": "5367422806881622213", "title": "King Dragon 👑🐉"},
    66: {"emoji_id": "5367422806881622214", "title": "King Dragon 👑🐉"},
    67: {"emoji_id": "5367422806881622215", "title": "King Dragon 👑🐉"},
    68: {"emoji_id": "5367422806881622216", "title": "King Dragon 👑🐉"},
    69: {"emoji_id": "5367422806881622217", "title": "King Dragon 👑🐉"},
    70: {"emoji_id": "5367422806881622218", "title": "King Dragon 👑🐉"},
}

# === VERİTABANI ===
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        print("✅ Veritabanı bağlantısı kuruldu")
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                messages_count INTEGER DEFAULT 0,
                last_message_date TEXT,
                joined_date TEXT
            )
        ''')
        self.conn.commit()
        print("✅ Tablolar oluşturuldu")
    
    def add_user(self, user_id, username, first_name, last_name):
        try:
            now = datetime.datetime.now().isoformat()
            self.cursor.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name, joined_date) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, now))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ add_user hatası: {e}")
            return False
    
    def update_user_activity(self, user_id):
        try:
            now = datetime.datetime.now().isoformat()
            
            self.cursor.execute('SELECT xp, level, messages_count FROM users WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            
            if result:
                xp, level, messages_count = result
                new_xp = xp + XP_PER_MESSAGE
                new_messages_count = messages_count + 1
                new_level = (new_xp // 100) + 1
                if new_level > 70:
                    new_level = 70
                
                self.cursor.execute('''
                    UPDATE users 
                    SET xp = ?, level = ?, messages_count = ?, last_message_date = ?
                    WHERE user_id = ?
                ''', (new_xp, new_level, new_messages_count, now, user_id))
                
                self.conn.commit()
                
                if new_level > level:
                    return True, new_level
            return False, None
        except Exception as e:
            print(f"❌ update_user_activity hatası: {e}")
            return False, None
    
    def get_user_stats(self, user_id):
        try:
            self.cursor.execute('''
                SELECT username, first_name, xp, level, messages_count, last_message_date 
                FROM users WHERE user_id = ?
            ''', (user_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"❌ get_user_stats hatası: {e}")
            return None
    
    def get_top_users(self, limit=10):
        try:
            self.cursor.execute('''
                SELECT user_id, username, first_name, xp, level, messages_count 
                FROM users 
                ORDER BY level DESC, xp DESC 
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ get_top_users hatası: {e}")
            return []
    
    def get_inactive_users_24h(self):
        try:
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
            
            self.cursor.execute('SELECT user_id, username, first_name FROM users')
            all_users = self.cursor.fetchall()
            
            self.cursor.execute('SELECT DISTINCT user_id FROM users WHERE last_message_date > ?', (yesterday,))
            active_users = set([row[0] for row in self.cursor.fetchall()])
            
            return [user for user in all_users if user[0] not in active_users]
        except Exception as e:
            print(f"❌ get_inactive_users_24h hatası: {e}")
            return []

db = Database()

# === BADÎNÎ ÇEVİRİLER ===
class BadiniTranslations:
    @staticmethod
    def bot_start_message():
        return "🔰 سوپاس ئەز بوتێ داتایێن گروپی مە. بۆ هاریکاریێ دشێی چێکی /help"
    
    @staticmethod
    def level_up_message(username, level):
        # Level'e göre emoji ve title al
        if level in EMOJI_CONFIG:
            title = EMOJI_CONFIG[level]["title"]
            emoji_config = EMOJI_CONFIG[level]["emoji_id"]
            
            # Emoji ID'sini mesaja ekle (Telegram premium emoji)
            if isinstance(emoji_config, list):
                emoji = f"<tg-emoji emoji-id=\"{emoji_config[0]}\">⭐</tg-emoji><tg-emoji emoji-id=\"{emoji_config[1]}\">⭐</tg-emoji>"
            else:
                emoji = f"<tg-emoji emoji-id=\"{emoji_config}\">⭐</tg-emoji>"
        else:
            # Varsayılan title'lar
            if level <= 10:
                title = "Diamond 💎"
                emoji = "💎"
            elif level <= 19:
                title = "Pro ⚡"
                emoji = "⚡"
            elif level <= 29:
                title = "Pro Leader 👑⚡"
                emoji = "👑⚡"
            elif level <= 39:
                title = "King 👑"
                emoji = "👑"
            elif level <= 49:
                title = "Dragon 🐉"
                emoji = "🐉"
            elif level <= 59:
                title = "Myth 🔱✨"
                emoji = "🔱✨"
            else:
                title = "King Dragon 👑🐉"
                emoji = "👑🐉"
        
        # Ana mesaj
        message = f"🎉 **LEVEL ATLADIN!** 🎉\n\n"
        message += f"{emoji} دەستخوش {username}!\n"
        message += f"تۆ گەهشتیە لیفل {level}\n"
        message += f"🏆 رتبە: **{title}**"
        
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
            message += "\n\n🏆 **MAX LEVEL!** تۆ گەهشتیە Level 70! 🏆"
        
        return message, emoji
    
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
            "24h": "⏰ /24h - کەسێن 24 سەعتاندا نە ئاخفتین (تەنێ ئادمین)",
            "nadmin": "👑 /nadmin - ڕێڤەبەرێن نوی ببینە (تەنێ ئادمین)"
        }
    
    @staticmethod
    def inactive_24h_report(inactive_list):
        if not inactive_list:
            return "📊 راپورا 24 سعەتان - هەمی ئاکتیڤن 🎉"
        
        message = "📊 راپورا 24 سعەتان - ئەو کەسێن 24 سعەتاندا نە ئاخفتین:\n\n"
        for user in inactive_list:
            user_id, username, first_name = user
            name = f"@{username}" if username else first_name
            message += f"• {name}\n"
        
        message += f"\n📊 کۆ: {len(inactive_list)} کەس"
        return message

translations = BadiniTranslations()

# === YARDIMCI FONKSİYONLAR ===
def update_admin_cache(chat_id):
    global admin_cache
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_cache = set([admin.user.id for admin in admins])
        print(f"✅ Admin cache: {len(admin_cache)} admin")
        for admin_id in admin_cache:
            print(f"   - Admin ID: {admin_id}")
    except Exception as e:
        print(f"❌ Admin cache hatası: {e}")

def is_allowed_group(message):
    if message.chat.type == 'private':
        return False
    return message.chat.id == ALLOWED_GROUP_ID

def get_user_display_name(user):
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    return "کاربەر"

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
    print(f"📌 /help - User: {message.from_user.id}")
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
    print(f"📌 /level - User: {message.from_user.id}")
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
            
            # Level'e göre title al
            if level in EMOJI_CONFIG:
                title = EMOJI_CONFIG[level]["title"]
            else:
                if level <= 10:
                    title = "Diamond 💎"
                elif level <= 19:
                    title = "Pro ⚡"
                elif level <= 29:
                    title = "Pro Leader 👑⚡"
                elif level <= 39:
                    title = "King 👑"
                elif level <= 49:
                    title = "Dragon 🐉"
                elif level <= 59:
                    title = "Myth 🔱✨"
                else:
                    title = "King Dragon 👑🐉"
            
            next_level_xp = (level * 100)
            xp_needed = next_level_xp - xp
            
            msg = f"📊 **LEVEL BİLGİLERİN**\n\n"
            msg += f"🏆 **Level:** {level} - {title}\n"
            msg += f"✨ **XP:** {xp}\n"
            
            if level < 70:
                msg += f"📈 **Sonraki Level:** {xp_needed} XP kaldı\n"
            
            bot.reply_to(message, msg)
        else:
            bot.reply_to(message, translations.error_message("no_user"))
    except Exception as e:
        print(f"❌ level hatası: {e}")
        bot.reply_to(message, translations.error_message("general"))

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    print(f"📌 /stats - User: {message.from_user.id}")
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
    print(f"📌 /top - User: {message.from_user.id}")
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, translations.error_message("wrong_group"))
            return
        
        top_users = db.get_top_users(10)
        
        if not top_users:
            bot.reply_to(message, "🏆 لیستا ڤاله‌یه - هێچ کاربەر نینە")
            return
        
        msg = "🏆 لیستا ڕیزبه‌ندیان\n\n"
        
        for i, user in enumerate(top_users, 1):
            user_id, username, first_name, xp, level, msg_count = user
            name = f"@{username}" if username else first_name
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            msg += f"{medal} {name}\n"
            msg += f"   • Level {level} | {xp} XP | {msg_count} نامە\n\n"
        
        bot.reply_to(message, msg)
    except Exception as e:
        print(f"❌ top hatası: {e}")
        bot.reply_to(message, translations.error_message("general"))

@bot.message_handler(commands=['24h'])
def cmd_24h(message):
    print(f"📌 /24h - User: {message.from_user.id}")
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
    print(f"📌 /nadmin - User: {message.from_user.id}")
    try:
        if not is_allowed_group(message):
            bot.reply_to(message, translations.error_message("wrong_group"))
            return
        
        if message.from_user.id not in admin_cache:
            bot.reply_to(message, translations.error_message("not_admin"))
            return
        
        update_admin_cache(message.chat.id)
        
        admin_list = "👑 ڕێڤەبەر:\n\n"
        for admin_id in admin_cache:
            try:
                user = bot.get_chat_member(message.chat.id, admin_id).user
                name = f"@{user.username}" if user.username else user.first_name
                admin_list += f"• {name}\n"
            except:
                admin_list += f"• ID: {admin_id}\n"
        
        bot.reply_to(message, f"👑 ڕێڤەبەر هاتنە دیتن: {len(admin_cache)} کەس\n\n{admin_list}")
    except Exception as e:
        print(f"❌ nadmin hatası: {e}")
        bot.reply_to(message, translations.error_message("general"))

@bot.message_handler(commands=['testid'])
def cmd_testid(message):
    print(f"📌 /testid - User: {message.from_user.id}")
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
        
        # Komutları tekrar kontrol et
        if message.text and message.text.startswith('/'):
            command = message.text.split()[0].lower()
            print(f"⚠️ Komut mesaj handler'ında: {command}")
            
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
        
        # Normal mesaj - XP ekle
        user = message.from_user
        db.add_user(user.id, user.username, user.first_name, user.last_name)
        
        leveled_up, new_level = db.update_user_activity(user.id)
        
        if leveled_up:
            name = get_user_display_name(user)
            level_msg, emoji = translations.level_up_message(name, new_level)
            
            # Premium emoji ile level atlama bildirimi
            if new_level in EMOJI_CONFIG:
                # HTML formatında premium emoji gönder
                bot.send_message(
                    message.chat.id,
                    f"🎉🎉🎉\n{level_msg}\n🎉🎉🎉",
                    parse_mode='HTML'
                )
            else:
                # Normal mesaj
                bot.send_message(
                    message.chat.id,
                    f"🎉🎉🎉\n{level_msg}\n🎉🎉🎉"
                )
            
            print(f"🎉 LEVEL UP! {name} -> Level {new_level}")
            
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
    print(f"📁 Veritabanı: {DB_NAME}")
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
