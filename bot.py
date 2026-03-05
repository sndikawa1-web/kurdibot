# Botê Analîzê yê Grupê - Badini Kürtçesi
# Sadece belirli grupta çalışır, Irak saatine göre gece 12:00'de rapor

import os
import json
import logging
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

# ==================== KONFİGÜRASYON ====================
TOKEN = os.environ.get('BOT_TOKEN')
GROUP_ID = int(os.environ.get('GROUP_ID', 0))  # Senin grup ID'n

# Irak Saati (UTC+3)
IRAQ_TZ = timezone(timedelta(hours=3))

# Loglama
logging.basicConfig(level=logging.INFO)

# ==================== BADİNİ KÜRTÇESİ MESAJLAR ====================
class BadiniMessages:
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
    PENALTY_1 = "جزا 1 نقتە"
    PENALTY_2 = "جزا 2 نقتە"
    PENALTY_3 = "ئەو کەسێت گەهشتین 3 جزایا"
    WARNING = "وژداری"
    
    # İstatistik
    MESSAGE = "نامە"
    MEMBER = "ئەندام"
    TOTAL = "کۆ"
    RANKING = "رێزبەندی"
    FIRST = "ێکەم"
    SECOND = "دویەم"
    THIRD = "سێیەم"
    
    # Komutlar
    REPORT = "📋 راپور"
    RELOAD = "🔄 بارکرن دوبارە"
    
    # Bildirimler
    CONGRATS = "🎉 دەستخوش"
    ATTENTION = "⚠️ اگهداری"
    SUCCESS = "✅ ب سەرکەڤتیانە"
    ERROR = "❌ خەلەتیەک چێبی"
    
    # Özel İfadeler
    NO_MESSAGES = "هیچ نامە رێنەکرە"
    MOST_ACTIVE = "ئەندامێ ژ هەمیان اکتیڤتر"
    TODAY_ACTIVE = "کەسێن ئەفرو نامە رێکرین"
    TODAY_SILENT = "کەسێن ئەفروکا بێدەنگ"
    PENALTY_CLEARED = "✅ جزایێ تە خلاس"
    
    # Örnek Cümleler
    INACTIVE_24H = "👤 د ماویێ 24 سعەتان دا ئەو کەسێن نە اخفتین:"
    PENALTY_3_LIST = "⚠️ ئەو کەسێن گەهشتین 3 جزایا:"
    RESET_PENALTY = "🔄 ب هنارتنا نامەکێ بو گروبی جزایێن خو ژێببە"
    WEEKLY_TOP = "👑 ئەندامێ د حەڤتیێ دا ژ هەمیان اکتیڤتر:"
    TODAY_STATS = "📊 ئەفروکە {} هندە نامە هاتن"
    MESSAGE_LIST = "📝 لیستا نامەیان:"
    
    # Admin Mesajları
    NOT_ADMIN = "⛔ تە دەستوری ئەمە نینە!"
    ADMIN_UPDATED = "✅ لیستا ئەدمینان هاتە تازەکرن!"
    ADMIN_UPDATING = "🔄 لیستا ئەدمینان تازە دبیت..."
    REPORT_PREPARING = "🚀 رەپورت هاتیە ئامادەکرن..."
    NEED_ADMIN = "⚠️ ئەز ئەدمین نیمە! تکایە ئەز بکە ئەدمین."
    
    # Özel mesajlar
    PRIVATE_CHAT_ERROR = "❌ ئەز تەنێ د گروپان دا کار دکەم! (Sadece gruplarda çalışırım)"
    WRONG_GROUP_ERROR = "❌ ئەز تەنێ بۆ گروپێ تایبەت کار دکەم! (Sadece özel grubumda çalışırım)"


# ==================== VERİTABANI ====================
class Database:
    def __init__(self):
        self.users_file = 'users.json'
        self.messages_file = 'messages.json'
        self.penalties_file = 'penalties.json'
        self.admins_file = 'admins.json'
        self.load_data()
    
    def load_data(self):
        for file in [self.users_file, self.messages_file, self.penalties_file, self.admins_file]:
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
        
        # Kullanıcıyı kaydet
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        users[user_id_str] = {
            'username': username or first_name,
            'first_name': first_name,
            'last_seen': datetime.now(IRAQ_TZ).isoformat()
        }
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        # Mesaj sayısını güncelle
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        if today not in messages:
            messages[today] = {}
        
        if user_id_str not in messages[today]:
            messages[today][user_id_str] = 0
        
        messages[today][user_id_str] += 1
        
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        # Eksiyi sıfırla (sadece admin değilse)
        if not self.is_admin(user_id):
            with open(self.penalties_file, 'r', encoding='utf-8') as f:
                penalties = json.load(f)
            
            penalties[user_id_str] = {
                'count': 0,
                'last_message': datetime.now(IRAQ_TZ).isoformat()
            }
            
            with open(self.penalties_file, 'w', encoding='utf-8') as f:
                json.dump(penalties, f, ensure_ascii=False, indent=2)
    
    def update_penalties(self):
        with open(self.penalties_file, 'r', encoding='utf-8') as f:
            penalties = json.load(f)
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        admins = self.get_admins()
        one_day_ago = datetime.now(IRAQ_TZ) - timedelta(days=1)
        
        for user_id, user_data in users.items():
            if user_id in admins:
                continue
                
            last_seen = datetime.fromisoformat(user_data.get('last_seen', '2000-01-01'))
            
            if last_seen < one_day_ago:
                if user_id not in penalties:
                    penalties[user_id] = {'count': 0, 'last_message': None}
                
                penalties[user_id]['count'] += 1
        
        with open(self.penalties_file, 'w', encoding='utf-8') as f:
            json.dump(penalties, f, ensure_ascii=False, indent=2)
        
        return penalties
    
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
                username = user_data.get('username', user_data.get('first_name', 'Bilinmiyor'))
                result.append((user_id, username))
        
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
                username = user_data.get('username', user_data.get('first_name', 'Bilinmiyor'))
                inactive.append(username)
        
        return inactive
    
    def get_all_users_message_counts_24h(self):
        """Son 24 saatte tüm kullanıcıların mesaj sayılarını getir"""
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
                    if count > 0:  # Sadece mesaj gönderenleri al
                        user_counts[user_id] = user_counts.get(user_id, 0) + count
        
        # Kullanıcı adlarıyla birlikte listele
        result = []
        for user_id, count in user_counts.items():
            user_data = users.get(user_id, {})
            username = user_data.get('username', user_data.get('first_name', 'Bilinmiyor'))
            result.append((username, count))
        
        # Mesaj sayısına göre sırala (çoktan aza)
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result


# ==================== ANA BOT ====================
class BadiniAnalizBot:
    def __init__(self, token):
        self.token = token
        self.db = Database()
        self.msgs = BadiniMessages()
        self.first_run = True
    
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
                
                # Gruba uyarı gönder
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
                    'username': user.username or user.first_name,
                    'first_name': user.first_name,
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
                    text=f"✅ **{self.msgs.BOT_NAME}**\n"
                         f"👮 {len(admin_dict)} ئەدمین هاتنە ناسین\n"
                         f"📊 24 سعەت رەپورت هەر شەڤ دێ هاتە\n"
                         f"📋 {self.msgs.REPORT} - تەنێ بو ئەدمینان\n"
                         f"🔄 {self.msgs.RELOAD} - تەنێ بو ئەدمینان\n\n"
                         f"⏰ کاتی عێراق: 12:00 شەڤ"
                )
            
        except Exception as e:
            logging.error(f"Admin güncelleme hatası: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start komutu - sadece grupta çalışır"""
        # Özel sohbet mi kontrol et
        if update.effective_chat.type == 'private':
            await update.message.reply_text(self.msgs.PRIVATE_CHAT_ERROR)
            return
        
        # Doğru grup mu kontrol et
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(self.msgs.WRONG_GROUP_ERROR)
            return
        
        await update.message.reply_text(
            f"👋 **{self.msgs.WELCOME}**\n\n"
            f"**{self.msgs.BOT_NAME}**\n\n"
            f"📊 داتایێن 24 سعەت و حەڤتیێ\n"
            f"⚠️ سیستمێ جزایێن بێدەنگیان\n\n"
            f"📋 {self.msgs.REPORT} - تەنێ بو ئەدمینان\n"
            f"🔄 {self.msgs.RELOAD} - تەنێ بو ئەدمینان\n\n"
            f"⏰ کاتی عێراق: 12:00 شەڤ"
        )
    
    async def rapor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/rapor komutu - sadece adminler için, sadece grupta"""
        # Özel sohbet mi kontrol et
        if update.effective_chat.type == 'private':
            await update.message.reply_text(self.msgs.PRIVATE_CHAT_ERROR)
            return
        
        # Doğru grup mu kontrol et
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(self.msgs.WRONG_GROUP_ERROR)
            return
        
        # Admin mi kontrol et
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        await update.message.reply_text(self.msgs.REPORT_PREPARING)
        
        # Tüm kullanıcıların mesaj sayılarını al
        all_users = self.db.get_all_users_message_counts_24h()
        inactive = self.db.get_inactive_users_24h()
        
        now = datetime.now(IRAQ_TZ)
        msg = f"**📊 {self.msgs.REPORT_24H}**\n\n"
        msg += f"⏰ **کاتی عێراق:** {now.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if all_users:
            msg += f"**📝 {self.msgs.MESSAGE_LIST}**\n"
            for i, (username, count) in enumerate(all_users, 1):
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = "📌"
                msg += f"{medal} **{username}** - {count} {self.msgs.MESSAGE}\n"
            
            msg += f"\n📊 **{self.msgs.TOTAL}:** {len(all_users)} {self.msgs.MEMBER}\n\n"
        else:
            msg += f"{self.msgs.NO_MESSAGES}\n\n"
        
        # Pasif kullanıcılar
        if inactive:
            msg += f"**💤 {self.msgs.INACTIVE_24H}**\n"
            for username in inactive[:10]:
                msg += f"• {username}\n"
        
        await update.message.reply_text(msg)
    
    async def reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/reload komutu - sadece adminler için, sadece grupta"""
        # Özel sohbet mi kontrol et
        if update.effective_chat.type == 'private':
            await update.message.reply_text(self.msgs.PRIVATE_CHAT_ERROR)
            return
        
        # Doğru grup mu kontrol et
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(self.msgs.WRONG_GROUP_ERROR)
            return
        
        # Admin mi kontrol et
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        await update.message.reply_text(self.msgs.ADMIN_UPDATING)
        await self.update_admins(context)
        await update.message.reply_text(self.msgs.ADMIN_UPDATED)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gelen mesajları işle - sadece doğru grupta"""
        # Sadece doğru grup
        if update.effective_chat.id != GROUP_ID:
            return
        
        user = update.effective_user
        if not user:
            return
        
        self.db.add_message(user.id, user.username, user.first_name)
    
    async def send_daily_report(self, context):
        """Günlük rapor gönder (otomatik) - Irak saati 00:00"""
        if not GROUP_ID:
            return
        
        now = datetime.now(IRAQ_TZ)
        
        # Tüm kullanıcıların mesaj sayılarını al
        all_users = self.db.get_all_users_message_counts_24h()
        inactive = self.db.get_inactive_users_24h()
        
        msg = f"**📊 {self.msgs.REPORT_24H}**\n\n"
        msg += f"⏰ **کاتی عێراق:** {now.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if all_users:
            msg += f"**📝 {self.msgs.MESSAGE_LIST}**\n"
            for i, (username, count) in enumerate(all_users, 1):
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = "📌"
                msg += f"{medal} **{username}** - {count} {self.msgs.MESSAGE}\n"
            
            msg += f"\n📊 **{self.msgs.TOTAL}:** {len(all_users)} {self.msgs.MEMBER}\n\n"
        else:
            msg += f"{self.msgs.NO_MESSAGES}\n\n"
        
        # Pasif kullanıcılar
        if inactive:
            msg += f"**💤 {self.msgs.INACTIVE_24H}**\n"
            for username in inactive[:10]:
                msg += f"• {username}\n"
        
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=msg
        )
    
    async def send_weekly_report(self, context):
        """Haftalık rapor gönder"""
        if not GROUP_ID:
            return
        
        now = datetime.now(IRAQ_TZ)
        all_users = self.db.get_all_users_message_counts_24h()  # 24 saatlik
        
        msg = f"**📈 {self.msgs.REPORT_WEEKLY}**\n\n"
        msg += f"⏰ **کاتی عێراق:** {now.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if all_users:
            msg += f"**👑 {self.msgs.MOST_ACTIVE}**\n"
            msg += f"**{all_users[0][0]}** - {all_users[0][1]} {self.msgs.MESSAGE}\n\n"
        
        penalties = self.db.get_users_with_3_penalties()
        if penalties:
            msg += f"**⚠️ {self.msgs.PENALTY_3_LIST}**\n"
            for user_id, username in penalties:
                msg += f"• {username}\n"
            
            msg += f"\n💡 {self.msgs.RESET_PENALTY}"
        
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=msg
        )
    
    async def check_penalties_job(self, context):
        """Eksileri kontrol et"""
        self.db.update_penalties()
        
        penalties = self.db.get_users_with_3_penalties()
        
        if penalties and GROUP_ID:
            msg = f"**⚠️ {self.msgs.PENALTY_3_LIST}**\n\n"
            for user_id, username in penalties:
                msg += f"• {username}\n"
            
            msg += f"\n💡 {self.msgs.RESET_PENALTY}"
            
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=msg
            )
    
    async def update_admins_job(self, context):
        """Zamanlanmış admin güncelleme"""
        await self.update_admins(context)
    
    def run(self):
        """Botu başlat"""
        application = Application.builder().token(self.token).build()
        
        # Komutlar - hepsi grup kontrolü yapacak
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("rapor", self.rapor_command))
        application.add_handler(CommandHandler("reload", self.reload_command))
        
        # Mesaj handler - sadece doğru gruptan mesajları işler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Bot başlarken adminleri güncelle
        async def init_admins(app):
            await self.update_admins(app)
        
        application.post_init = init_admins
        
        # Zamanlanmış görevler - Irak saatine göre
        job_queue = application.job_queue
        
        if job_queue:
            # Her gün adminleri güncelle (Irak saati 03:00)
            job_queue.run_daily(
                self.update_admins_job,
                time=datetime.time(hour=3, minute=0, tzinfo=IRAQ_TZ)
            )
            
            # Her gün eksileri kontrol et (Irak saati 00:30)
            job_queue.run_daily(
                self.check_penalties_job,
                time=datetime.time(hour=0, minute=30, tzinfo=IRAQ_TZ)
            )
            
            # Her gün rapor gönder (Irak saati 00:00 - GECE 12)
            job_queue.run_daily(
                self.send_daily_report,
                time=datetime.time(hour=0, minute=0, tzinfo=IRAQ_TZ)
            )
            
            # Her Pazar haftalık rapor (Irak saati 00:00)
            job_queue.run_daily(
                self.send_weekly_report,
                time=datetime.time(hour=0, minute=0, tzinfo=IRAQ_TZ),
                days=(6,)  # Pazar
            )
        
        print(f"🚀 {self.msgs.BOT_NAME} başladı...")
        print(f"📊 Grup ID: {GROUP_ID}")
        print(f"⏰ Irak Saati: {datetime.now(IRAQ_TZ).strftime('%H:%M')}")
        print(f"📋 Komutlar: /start, /rapor (admin), /reload (admin)")
        print(f"⏱ Otomatik rapor: Her gece 00:00 Irak saati")
        application.run_polling()


# ==================== BAŞLAT ====================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ HATA: BOT_TOKEN bulunamadı!")
        exit(1)
    
    if not GROUP_ID:
        print("⚠️ UYARI: GROUP_ID tanımlanmamış!")
    
    bot = BadiniAnalizBot(TOKEN)
    bot.run()
