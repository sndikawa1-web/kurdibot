# bot.py - TAM ÇALIŞAN VERSİYON
import telebot
import os
import sqlite3
import datetime
from telebot import types

# === KONFİGÜRASYON ===
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
ALLOWED_GROUP_ID = int(os.environ.get('GROUP_ID', '0'))
DB_NAME = "badini_bot.db"
XP_PER_MESSAGE = 10

# Bot'u başlat
bot = telebot.TeleBot(BOT_TOKEN)

# Admin cache
admin_cache = set()

# === VERİTABANI ===
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
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
    
    def add_user(self, user_id, username, first_name, last_name):
        now = datetime.datetime.now().isoformat()
        self.cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, last_name, joined_date) 
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, now))
        self.conn.commit()
    
    def update_user_activity(self, user_id):
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
    
    def get_user_stats(self, user_id):
        self.cursor.execute('''
            SELECT username, first_name, xp, level, messages_count, last_message_date 
            FROM users WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchone()
    
    def get_top_users(self, limit=10):
        self.cursor.execute('''
            SELECT user_id, username, first_name, xp, level, messages_count 
            FROM users 
            ORDER BY level DESC, xp DESC 
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_inactive_users_24h(self):
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
        
        self.cursor.execute('SELECT user_id, username, first_name FROM users')
        all_users = self.cursor.fetchall()
        
        self.cursor.execute('SELECT DISTINCT user_id FROM users WHERE last_message_date > ?', (yesterday,))
        active_users = set([row[0] for row in self.cursor.fetchall()])
        
        return [user for user in all_users if user[0] not in active_users]

db = Database()

# === BADÎNÎ ÇEVİRİLER ===
class BadiniTranslations:
    @staticmethod
    def bot_start_message():
        return "🔰 سوپاس ئەز بوتێ داتایێن گروپی مە. بۆ هاریکاریێ دشێی چێکی /help"
    
    @staticmethod
    def level_up_message(username, level):
        return f"🎉 دەستخوش {username} گەهشتیە لیفل {level}!"
    
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
            "level": "📊 /level - لیفلێ خۆ و XP'yê نیشان بدە",
            "stats": "📈 /stats - داتایێن خۆ نیشان بدە",
            "top": "🏆 /top - ئەندامێن بیلیفتا هەرێ بلند",
            "24h": "⏰ /24h - کەسێن 24 سەعتاندا نە ئاخفتین (ئادمین)",
            "nadmin": "👑 /nadmin - ڕێڤەبەرێن نوی ببینە (ئادمین)"
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
        
        message += f"\nئەو کەسێن نە ئاخفتین: {len(inactive_list)} کەس"
        return message

translations = BadiniTranslations()

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

def get_user_display_name(user):
    if user.username:
        return f"@{user.username}"
    elif user.first_name:
        return user.first_name
    return "Kullanıcı"

# === KOMUTLAR ===
@bot.message_handler(commands=['start'])
def cmd_start(message):
    print(f"/start: {message.from_user.id}")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    bot.reply_to(message, translations.bot_start_message(), parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def cmd_help(message):
    print(f"/help")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    help_text = "**📋 فرمانێن بوت:**\n\n"
    for cmd, desc in translations.command_descriptions().items():
        help_text += f"{desc}\n"
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['level', 'stats'])
def cmd_level(message):
    print(f"/level")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    user_id = message.from_user.id
    stats = db.get_user_stats(user_id)
    
    if not stats:
        # Kullanıcı yoksa ekle
        user = message.from_user
        db.add_user(user_id, user.username, user.first_name, user.last_name)
        stats = db.get_user_stats(user_id)
    
    if stats:
        username, first_name, xp, level, msg_count, last_date = stats
        name = f"@{username}" if username else first_name
        
        # Level title
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
        
        msg = (
            f"📊 **داتایێن {name}**\n\n"
            f"🏆 **Level:** {level} - {title}\n"
            f"✨ **XP:** {xp}\n"
            f"💬 **نامه:** {msg_count}\n"
        )
        
        if level < 70:
            msg += f"📈 **بۆ لیفلەکێ نڤ:** {xp_needed} XP"
        
        if last_date:
            msg += f"\n⏰ **دوماهیک نامە:** {last_date[:10]}"
        
        bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['top'])
def cmd_top(message):
    print(f"/top")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    top_users = db.get_top_users(10)
    
    if not top_users:
        bot.reply_to(message, "🏆 لیستا ڤاله‌یه")
        return
    
    msg = "🏆 **لیستا ڕیزبه‌ندیان**\n\n"
    
    for i, user in enumerate(top_users, 1):
        user_id, username, first_name, xp, level, msg_count = user
        name = f"@{username}" if username else first_name
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        msg += f"{medal} **{name}**\n"
        msg += f"   • Level {level} | {xp} XP | {msg_count} نامه\n\n"
    
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['24h'])
def cmd_24h(message):
    print(f"/24h")
    if not is_allowed_group(message):
        bot.reply_to(message, translations.error_message("wrong_group"))
        return
    
    if message.from_user.id not in admin_cache:
        bot.reply_to(message, translations.error_message("not_admin"))
        return
    
    inactive_users = db.get_inactive_users_24h()
    report = translations.inactive_24h_report(inactive_users)
    bot.reply_to(message, report, parse_mode='Markdown')

@bot.message_handler(commands=['nadmin'])
def cmd_nadmin(message):
    print(f"/nadmin")
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
    print(f"/testid")
    if message.chat.type == 'private':
        bot.reply_to(message, "Bu özel sohbet")
        return
    
    # Admin mi kontrol et
    is_admin = message.from_user.id in admin_cache
    
    msg = (
        f"📊 **GRUP BİLGİLERİ**\n\n"
        f"🆔 Grup ID: `{message.chat.id}`\n"
        f"🔑 İzin verilen: `{ALLOWED_GROUP_ID}`\n"
        f"✅ Eşleşiyor: {'✅' if message.chat.id == ALLOWED_GROUP_ID else '❌'}\n"
        f"👤 Sizin ID: `{message.from_user.id}`\n"
        f"👑 Admin: {'✅' if is_admin else '❌'}\n"
        f"📊 Toplam admin: {len(admin_cache)}"
    )
    bot.reply_to(message, msg, parse_mode='Markdown')

# === MESAJ İŞLEYİCİ ===
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    if not is_allowed_group(message):
        return
    
    user = message.from_user
    
    # Kullanıcıyı ekle
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    # XP ekle
    leveled_up, new_level = db.update_user_activity(user.id)
    
    if leveled_up:
        name = get_user_display_name(user)
        level_msg = translations.level_up_message(name, new_level)
        bot.reply_to(message, level_msg)

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
        else:
            # Yeni üye
            db.add_user(new_member.id, new_member.username, new_member.first_name, new_member.last_name)

# === ANA ÇALIŞTIRMA ===
if __name__ == "__main__":
    print("🤖 BOT BAŞLATILIYOR...")
    print(f"Token: {BOT_TOKEN[:10]}...")
    print(f"Grup ID: {ALLOWED_GROUP_ID}")
    
    # Admin cache'i güncelle
    try:
        update_admin_cache(ALLOWED_GROUP_ID)
    except Exception as e:
        print(f"⚠️ Admin cache alınamadı: {e}")
    
    print("🚀 Polling başlıyor...")
    print("✅ Komutlar hazır: /start, /help, /level, /stats, /top, /24h, /nadmin, /testid")
    bot.infinity_polling()
