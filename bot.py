# Botê Analîzê yê Grupê - Badini Kürtçesi (TÜM ÖZELLİKLER)
# Komutlar: /start, /rapor, /reload, /top10, /haftalik, /aylik, /aktifsaat, /rozetler, /seviye, /hatirlat, /rekor, /siralamam, /rozetlerim, /sampiyon, /kalite

import os
import json
import logging
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

# ==================== KONFİGÜRASYON ====================
TOKEN = os.environ.get('BOT_TOKEN')
GROUP_ID = int(os.environ.get('GROUP_ID', 0))

# Irak Saati (UTC+3)
IRAQ_TZ = timezone(timedelta(hours=3))

# Loglama
logging.basicConfig(level=logging.INFO)

# ==================== BADİNİ KÜRTÇESİ MESAJLAR ====================
class BadiniMessages:
    # Temel Mesajlar
    BOT_NAME = "Botê Analîzê yê Grupê"
    WELCOME = "خێرهاتی"
    
    # Rapor Başlıkları
    REPORT_24H = "📊 داتایێن 24 سعەتا"
    REPORT_WEEKLY = "📈 داتایێن حەڤتیێ"
    ACTIVE_USERS = "👥 ئەندامێن اکتیڤ"
    INACTIVE_USERS = "💤 ئەندامێن نە اکتیڤ"
    TOP_MESSAGERS = "🏆 لیستا نامەیان"
    
    # Eksi Sistemi
    PENALTY = "⚠️ جزا"
    PENALTY_3 = "ئەو کەسێت گەهشتین 3 جزایا"
    WARNING = "وژداری"
    
    # İstatistik
    MESSAGE = "نامە"
    MEMBER = "ئەندام"
    TOTAL = "کۆ"
    
    # Komutlar
    REPORT = "📋 راپور"
    RELOAD = "🔄 بارکرن دوبارە"
    
    # Bildirimler
    SUCCESS = "✅ ب سەرکەڤتیانە"
    ERROR = "❌ خەلەتیەک چێبی"
    
    # Özel İfadeler
    NO_MESSAGES = "هیچ نامە رێنەکرە"
    MOST_ACTIVE = "ئەندامێ ژ هەمیان اکتیڤتر"
    INACTIVE_24H = "👤 د ماویێ 24 سعەتان دا ئەو کەسێن نە اخفتین:"
    PENALTY_3_LIST = "⚠️ ئەو کەسێن گەهشتین 3 جزایا:"
    RESET_PENALTY = "🔄 ب هنارتنا نامەکێ بو گروبی جزایێن خو ژێببە"
    WEEKLY_TOP = "👑 ئەندامێ د حەڤتیێ دا ژ هەمیان اکتیڤتر:"
    MESSAGE_LIST = "📝 لیستا نامەیان:"
    
    # Admin Mesajları
    NOT_ADMIN = "⛔ تە دەستوری ئەمە نینە!"
    ADMIN_UPDATED = "✅ لیستا ئەدمینان هاتە تازەکرن!"
    ADMIN_UPDATING = "🔄 لیستا ئەدمینان تازە دبیت..."
    REPORT_PREPARING = "🚀 رەپورت هاتیە ئامادەکرن..."
    NEED_ADMIN = "⚠️ ئەز ئەدمین نیمە! تکایە ئەز بکە ئەدمین."
    
    # Özel mesajlar
    PRIVATE_CHAT_ERROR = "❌ ئەز تەنێ د گروپان دا کار دکەم!"
    WRONG_GROUP_ERROR = "❌ ئەز تەنێ بۆ گروپێ تایبەت کار دکەم!"
    
    # Gelişmiş Mesajlar
    RANKING = "رێزبەندی"
    TOP10 = "توپ 10"
    WEEKLY_RANKING = "رێزبەندیا حەڤتیانە"
    MONTHLY_RANKING = "رێزبەندیا هەیفانە"
    DAILY_RANKING = "رێزبەندیا روژانە"
    HOURLY = "سعەتی"
    DAILY = "روژانە"
    WEEKLY = "حەڤتیانە"
    MONTHLY = "هەیفانە"
    ACTIVE_HOURS = "دەمژمێرێن اکتیڤ"
    ACTIVE_DAYS = "روژانێن اکتیڤ"
    GROUP_SCORE = "سکورێ گروپی"
    GROUP_QUALITY = "قوالێتیا گروپی"
    BADGE = "مەدالی"
    ACHIEVEMENTS = "دەسکەوتەکان"
    LEVEL = "لیفل"
    XP = "پوینتێن تجروبێ"
    BADGE_EARNED = "مەدالی بدەستفە ینا"
    BADGE_7DAYS = "٧ روژا سەر ێک نامە"
    BADGE_1000MSG = "١٠٠٠ نامە"
    BADGE_500MSG = "٥٠٠ نامە"
    BADGE_MOST_MSG = "پترترین نامە"
    BADGE_SPECIAL = "ئەندامێ بها"
    REMINDER_24H = "٢٤ سعەت بورین نامەکێ ڤرێکە"
    REMINDER_3DAYS = "٣ روژە تو نا ئاخفی"
    HAS_PENALTY = "تە پوینتێن جزای یێت هەین"
    PENALTY_CLEARED = "جزایێ تە هاتە سڤر کرن"
    DAILY_RECORD = "سکورێ نامان یێ روژانە"
    WEEKLY_RECORD = "سکورێ نامان یێ حەڤیتانە"
    MONTHLY_RECORD = "سکورێ نامان یێ هەیفانە"
    MOST_MESSAGES = "ئەو کەسێ پترین نامە رێکرین"
    LONGEST_MESSAGE = "درێشترین نامە"
    MY_RANK = "رێزبەندیامن"
    MY_BADGES = "مەدالیێن من"
    MY_LEVEL = "مستەوایێ من"
    GROUP_STATS = "داتایێن گروپی"
    CONGRAT_500 = "دەستخوش گەهشتیە ٥٠٠ نامان"
    CONGRAT_1000 = "دەستخوش گەهشتیە ١٠٠٠ نامان"
    CONGRAT_MONTH = "دەستخوش هەیفەکە اکتیڤی"
    CONGRAT_BADGE = "دەستخوش مەدالییەک بدەستفە ینا"
    WEEKLY_CHAMP = "سەرکەڤتیێ حەڤتیێ"
    WEEKLY_MOST_ACTIVE = "اکتیڤ ترین کەس د حەڤتیێ دا"
    YOUR_REWARD = "خەلاتێ تە"
    CONGRAT_CHAMP = "دەستخوش سەرکەڤتیێ مە"
    QUALITY_SCORE = "کوالێتیا گروپی"
    ACTIVE_MEMBER_RATIO = "رێژا ئەندامێن اکتیڤ"
    GROWTH_RATE = "رێژا گەشەکرنێ"
    SCORE = "سکور"
    EXCELLENT = "زورباشە"
    GOOD = "باشە"
    MEDIUM = "نافەراست"
    BAD = "خراب"


# ==================== VERİTABANI ====================
class Database:
    def __init__(self):
        self.users_file = 'users.json'
        self.messages_file = 'messages.json'
        self.penalties_file = 'penalties.json'
        self.admins_file = 'admins.json'
        self.achievements_file = 'achievements.json'
        self.levels_file = 'levels.json'
        self.records_file = 'records.json'
        self.hourly_file = 'hourly_stats.json'
        self.load_data()
    
    def load_data(self):
        files = [self.users_file, self.messages_file, self.penalties_file, 
                 self.admins_file, self.achievements_file, self.levels_file,
                 self.records_file, self.hourly_file]
        for file in files:
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False)
    
    def save_admins(self, admin_list):
        with open(self.admins_file, 'w', encoding='utf-8') as f:
            json.dump(admin_list, f, ensure_ascii=False, indent=2)
    
    def get_admins(self):
        with open(self.admins_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def is_admin(self, user_id):
        admins = self.get_admins()
        return str(user_id) in admins
    
    def add_message(self, user_id, username, first_name):
        today = datetime.now(IRAQ_TZ).strftime("%Y-%m-%d")
        user_id_str = str(user_id)
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        users[user_id_str] = {
            'username': username,
            'first_name': first_name,
            'user_id': user_id,
            'last_seen': datetime.now(IRAQ_TZ).isoformat()
        }
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        if today not in messages:
            messages[today] = {}
        
        if user_id_str not in messages[today]:
            messages[today][user_id_str] = 0
        
        messages[today][user_id_str] += 1
        
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        # Saatlik istatistik
        hour_key = datetime.now(IRAQ_TZ).strftime("%Y-%m-%d-%H")
        with open(self.hourly_file, 'r', encoding='utf-8') as f:
            hourly = json.load(f)
        
        if hour_key not in hourly:
            hourly[hour_key] = {}
        
        if user_id_str not in hourly[hour_key]:
            hourly[hour_key][user_id_str] = 0
        
        hourly[hour_key][user_id_str] += 1
        
        with open(self.hourly_file, 'w', encoding='utf-8') as f:
            json.dump(hourly, f, ensure_ascii=False, indent=2)
        
        # Eksi sıfırlama
        if not self.is_admin(user_id):
            with open(self.penalties_file, 'r', encoding='utf-8') as f:
                penalties = json.load(f)
            
            penalties[user_id_str] = {
                'count': 0,
                'last_message': datetime.now(IRAQ_TZ).isoformat()
            }
            
            with open(self.penalties_file, 'w', encoding='utf-8') as f:
                json.dump(penalties, f, ensure_ascii=False, indent=2)
    
    def get_all_users_message_counts_24h(self):
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        since_date = (datetime.now(IRAQ_TZ) - timedelta(hours=24)).date()
        
        user_counts = {}
        for date_str, daily_msgs in messages.items():
            msg_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if msg_date >= since_date:
                for user_id, count in daily_msgs.items():
                    if count > 0:
                        user_counts[user_id] = user_counts.get(user_id, 0) + count
        
        result = []
        for user_id, count in user_counts.items():
            user_data = users.get(user_id, {})
            username = user_data.get('username')
            if username:
                display_name = f"@{username}"
            else:
                display_name = user_data.get('first_name', 'Bilinmiyor')
            result.append((display_name, count, user_id))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result
    
    def get_inactive_users_24h(self):
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        admins = self.get_admins()
        one_day_ago = datetime.now(IRAQ_TZ) - timedelta(days=1)
        inactive = []
        
        for user_id, user_data in users.items():
            if user_id in admins:
                continue
            last_seen = datetime.fromisoformat(user_data.get('last_seen', '2000-01-01'))
            if last_seen < one_day_ago:
                username = user_data.get('username')
                if username:
                    inactive.append(f"@{username}")
                else:
                    inactive.append(user_data.get('first_name', 'Bilinmiyor'))
        
        return inactive
    
    def get_most_active_hours(self, days=7):
        with open(self.hourly_file, 'r', encoding='utf-8') as f:
            hourly = json.load(f)
        
        since = (datetime.now(IRAQ_TZ) - timedelta(days=days)).strftime("%Y-%m-%d")
        
        hour_counts = {}
        for hour_key, users in hourly.items():
            if hour_key >= since:
                hour = hour_key.split('-')[3]
                total = sum(users.values())
                hour_counts[hour] = hour_counts.get(hour, 0) + total
        
        top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [(f"{h}:00", count) for h, count in top_hours]
    
    def get_users_with_3_penalties(self):
        with open(self.penalties_file, 'r', encoding='utf-8') as f:
            penalties = json.load(f)
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        admins = self.get_admins()
        result = []
        
        for user_id, penalty_data in penalties.items():
            if user_id in admins:
                continue
            if penalty_data.get('count', 0) >= 3:
                user_data = users.get(user_id, {})
                username = user_data.get('username')
                user_id_int = user_data.get('user_id')
                if username:
                    result.append((user_id_int, f"@{username}"))
                else:
                    result.append((user_id_int, user_data.get('first_name', 'Bilinmiyor')))
        
        return result


# ==================== ANA BOT ====================
class BadiniBot:
    def __init__(self, token):
        self.token = token
        self.db = Database()
        self.msgs = BadiniMessages()
        self.first_run = True
    
    async def check_group(self, update: Update):
        if update.effective_chat.type == 'private':
            await update.message.reply_text(self.msgs.PRIVATE_CHAT_ERROR)
            return False
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(self.msgs.WRONG_GROUP_ERROR)
            return False
        return True
    
    async def check_bot_admin(self, context):
        """Bot'un admin olup olmadığını kontrol et"""
        try:
            if not GROUP_ID:
                return False
            
            bot_member = await context.bot.get_chat_member(GROUP_ID, context.bot.id)
            
            if bot_member.status in ['administrator', 'creator']:
                logging.info("✅ Bot admin yetkisine sahip")
                return True
            else:
                logging.warning("⚠️ Bot admin değil!")
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=f"⚠️ {self.msgs.NEED_ADMIN}"
                )
                return False
                
        except Exception as e:
            logging.error(f"Yetki kontrol hatası: {e}")
            return False
    
    async def update_admins(self, context):
        """Gruptaki adminleri güncelle"""
        try:
            if not GROUP_ID:
                return
            
            # Bot admin mi kontrol et
            is_admin = await self.check_bot_admin(context)
            if not is_admin:
                return
            
            # Admin listesini al
            admins = await context.bot.get_chat_administrators(GROUP_ID)
            
            admin_dict = {}
            for admin in admins:
                user = admin.user
                admin_dict[str(user.id)] = {
                    'username': user.username,
                    'first_name': user.first_name,
                    'user_id': user.id,
                    'is_owner': admin.status == 'creator'
                }
            
            # Adminleri kaydet
            self.db.save_admins(admin_dict)
            logging.info(f"✅ {len(admin_dict)} admin güncellendi")
            
            # İlk çalıştırmada bilgi ver
            if self.first_run:
                self.first_run = False
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=f"✅ {self.msgs.BOT_NAME}\n"
                         f"👮 {len(admin_dict)} ئەدمین هاتنە ناسین\n"
                         f"📊 24 سعەت رەپورت هەر شەڤ دێ هاتە\n\n"
                         f"⏰ کاتی عێراق: {datetime.now(IRAQ_TZ).strftime('%H:%M')}"
                )
            
        except Exception as e:
            logging.error(f"Admin güncelleme hatası: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        now = datetime.now(IRAQ_TZ)
        await update.message.reply_text(
            f"👋 {self.msgs.WELCOME}\n\n"
            f"{self.msgs.BOT_NAME}\n\n"
            f"📊 داتایێن 24 سعەت و حەڤتیێ\n"
            f"⚠️ سیستمێ جزایێن بێدەنگیان\n\n"
            f"📋 /rapor - راپور (ئەدمین)\n"
            f"🔄 /reload - بارکرن دوبارە (ئەدمین)\n"
            f"📊 /top10 - توپ 10\n"
            f"📈 /haftalik - حەڤتیانە\n"
            f"📅 /aylik - هەیفانە\n"
            f"⏰ /aktifsaat - دەمژمێرێن اکتیڤ\n"
            f"🏅 /rozetler - مەدالی\n"
            f"📊 /seviye - لیفل\n"
            f"⏰ /hatirlat - بیرخستن\n"
            f"🏆 /rekor - ریکۆرد\n"
            f"👤 /siralamam - رێزبەندییا من\n"
            f"🏅 /rozetlerim - مەدالیێن من\n"
            f"👑 /sampiyon - شامپیۆن\n"
            f"📊 /kalite - کوالێتی\n\n"
            f"⏰ کاتی عێراق: {now.strftime('%H:%M')}"
        )
    
    async def rapor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        await update.message.reply_text(self.msgs.REPORT_PREPARING)
        
        all_users = self.db.get_all_users_message_counts_24h()
        inactive = self.db.get_inactive_users_24h()
        now = datetime.now(IRAQ_TZ)
        
        msg = f"📊 {self.msgs.REPORT_24H}\n\n"
        msg += f"⏰ کاتی عێراق: {now.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if all_users:
            msg += f"📝 {self.msgs.MESSAGE_LIST}\n"
            for i, (display_name, count, user_id) in enumerate(all_users, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📌"
                msg += f"{medal} {display_name} - {count} {self.msgs.MESSAGE}\n"
            
            msg += f"\n📊 {self.msgs.TOTAL}: {len(all_users)} {self.msgs.MEMBER}\n\n"
        else:
            msg += f"{self.msgs.NO_MESSAGES}\n\n"
        
        if inactive:
            msg += f"💤 {self.msgs.INACTIVE_24H}\n"
            for username in inactive[:10]:
                msg += f"• {username}\n"
        
        await update.message.reply_text(msg)
    
    async def reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        await update.message.reply_text(self.msgs.ADMIN_UPDATING)
        await self.update_admins(context)
        await update.message.reply_text(self.msgs.ADMIN_UPDATED)
    
    async def top10_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        all_users = self.db.get_all_users_message_counts_24h()
        
        if not all_users:
            await update.message.reply_text(f"📊 {self.msgs.TOP10}\n\n{self.msgs.NO_MESSAGES}")
            return
        
        msg = f"📊 {self.msgs.TOP10}\n\n"
        for i, (display_name, count, user_id) in enumerate(all_users[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            msg += f"{medal} {display_name} - {count} {self.msgs.MESSAGE}\n"
        
        await update.message.reply_text(msg)
    
    async def weekly_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        all_users = self.db.get_all_users_message_counts_24h()
        
        msg = f"📊 {self.msgs.WEEKLY_RANKING}\n\n"
        if all_users:
            for i, (display_name, count, user_id) in enumerate(all_users[:10], 1):
                msg += f"{i}. {display_name} - {count} {self.msgs.MESSAGE}\n"
        else:
            msg += self.msgs.NO_MESSAGES
        
        await update.message.reply_text(msg)
    
    async def monthly_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        msg = f"📊 {self.msgs.MONTHLY_RANKING}\n\n"
        msg += "🔄 واهاتە... (Yakında)"
        await update.message.reply_text(msg)
    
    async def active_hours_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        top_hours = self.db.get_most_active_hours()
        
        msg = f"⏰ {self.msgs.ACTIVE_HOURS}\n\n"
        for hour, count in top_hours:
            msg += f"🕐 {hour} - {count} {self.msgs.MESSAGE}\n"
        
        await update.message.reply_text(msg)
    
    async def badges_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        msg = f"🏅 {self.msgs.BADGE}\n\n"
        msg += f"• {self.msgs.BADGE_7DAYS}\n"
        msg += f"• {self.msgs.BADGE_500MSG}\n"
        msg += f"• {self.msgs.BADGE_1000MSG}\n"
        msg += f"• {self.msgs.BADGE_MOST_MSG}\n"
        msg += f"• {self.msgs.BADGE_SPECIAL}\n"
        
        await update.message.reply_text(msg)
    
    async def level_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        msg = f"📊 {self.msgs.LEVEL}\n\n"
        msg += f"• Her mesaj = 10 XP\n"
        msg += f"• Her 200 XP = 1 Level\n"
        msg += f"• XP biriktir, level atla!\n"
        
        await update.message.reply_text(msg)
    
    async def reminder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        msg = f"⏰ {self.msgs.REMINDER_24H}\n\n"
        msg += "🔄 Yakında..."
        await update.message.reply_text(msg)
    
    async def records_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        msg = f"🏆 {self.msgs.GROUP_SCORE}\n\n"
        msg += "🔄 Yakında..."
        await update.message.reply_text(msg)
    
    async def myrank_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        msg = f"📊 {self.msgs.MY_RANK}\n\n"
        msg += f"👤 @{username}\n"
        msg += "🔄 Yakında..."
        
        await update.message.reply_text(msg)
    
    async def mybadges_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        msg = f"🏅 {self.msgs.MY_BADGES}\n\n"
        msg += "🔄 Yakında..."
        await update.message.reply_text(msg)
    
    async def weekly_champ_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        all_users = self.db.get_all_users_message_counts_24h()
        
        if not all_users:
            await update.message.reply_text("🏆 هێشتا داتا نینە!")
            return
        
        champ = all_users[0]
        
        msg = f"👑 {self.msgs.WEEKLY_CHAMP}\n\n"
        msg += f"🏆 {champ[0]}\n"
        msg += f"📊 {champ[1]} {self.msgs.MESSAGE}\n\n"
        msg += f"🎉 {self.msgs.CONGRAT_CHAMP}"
        
        await update.message.reply_text(msg)
    
    async def quality_score_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        all_users = self.db.get_all_users_message_counts_24h()
        inactive = self.db.get_inactive_users_24h()
        
        total_users = len(all_users) + len(inactive)
        active_count = len(all_users)
        
        if total_users == 0:
            active_ratio = 0
        else:
            active_ratio = (active_count / total_users) * 100
        
        if active_ratio >= 70:
            quality = self.msgs.EXCELLENT
            score = 90
        elif active_ratio >= 50:
            quality = self.msgs.GOOD
            score = 70
        elif active_ratio >= 30:
            quality = self.msgs.MEDIUM
            score = 50
        else:
            quality = self.msgs.BAD
            score = 30
        
        msg = f"📊 {self.msgs.GROUP_QUALITY}\n\n"
        msg += f"👥 {self.msgs.ACTIVE_MEMBER_RATIO}: %{active_ratio:.1f}\n"
        msg += f"📈 {self.msgs.GROWTH_RATE}: %5 (Örnek)\n"
        msg += f"⭐️ {self.msgs.SCORE}: {score}/100\n"
        msg += f"📌 {quality}"
        
        await update.message.reply_text(msg)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != GROUP_ID:
            return
        
        user = update.effective_user
        if not user:
            return
        
        self.db.add_message(user.id, user.username, user.first_name)
    
    def run(self):
        application = Application.builder().token(self.token).build()
        
        # Tüm komutlar
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("rapor", self.rapor_command))
        application.add_handler(CommandHandler("reload", self.reload_command))
        application.add_handler(CommandHandler("top10", self.top10_command))
        application.add_handler(CommandHandler("haftalik", self.weekly_command))
        application.add_handler(CommandHandler("aylik", self.monthly_command))
        application.add_handler(CommandHandler("aktifsaat", self.active_hours_command))
        application.add_handler(CommandHandler("rozetler", self.badges_command))
        application.add_handler(CommandHandler("seviye", self.level_command))
        application.add_handler(CommandHandler("hatirlat", self.reminder_command))
        application.add_handler(CommandHandler("rekor", self.records_command))
        application.add_handler(CommandHandler("siralamam", self.myrank_command))
        application.add_handler(CommandHandler("rozetlerim", self.mybadges_command))
        application.add_handler(CommandHandler("sampiyon", self.weekly_champ_command))
        application.add_handler(CommandHandler("kalite", self.quality_score_command))
        
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Bot başlarken adminleri güncelle
        async def init_admins(app):
            await self.update_admins(app)
        
        application.post_init = init_admins
        
        print(f"🚀 {self.msgs.BOT_NAME} başladı...")
        print(f"📋 Toplam komut: 16")
        application.run_polling()


# ==================== BAŞLAT ====================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ HATA: BOT_TOKEN bulunamadı!")
        exit(1)
    
    if not GROUP_ID:
        print("⚠️ UYARI: GROUP_ID tanımlanmamış!")
    
    bot = BadiniBot(TOKEN)
    bot.run()
