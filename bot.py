# Botê Analîzê yê Grupê - Badini Kürtçesi
# Adminleri otomatik tanır, analizler otomatik paylaşılır

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, ChatMemberAdministrator, ChatMemberOwner
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

# ==================== KONFİGÜRASYON ====================
TOKEN = os.environ.get('BOT_TOKEN')  # Telegram'dan aldığınız token
GROUP_ID = int(os.environ.get('GROUP_ID', 0))  # Grup ID'si

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
    TOP_MESSAGERS = "🏆 ئەو کەسێن گەلەك نامە رێکرین"
    
    # Eksi Sistemi
    PENALTY_3 = "⚠️ ئەو کەسێت گەهشتین 3 جزایا"
    
    # İstatistik
    MESSAGE = "نامە"
    TOTAL = "توتال"
    
    # Bildirimler
    CONGRATS = "🎉 دەستخوش"
    ATTENTION = "⚠️ اگهداری"
    SUCCESS = "✅ ب سەرکەڤتیانە"
    ERROR = "❌ خەلەتیەک چێبی"
    
    # Özel İfadeler
    INACTIVE_24H = "👤 د ماویێ 24 سعەتان دا ئەو کەسێن نە اخفتین:"
    PENALTY_3_LIST = "⚠️ ئەو کەسێن گەهشتین 3 جزایا:"
    RESET_PENALTY = "🔄 ب هنارتنا نامەکێ بو گروبی جزایێن خو ژێببە"
    WEEKLY_TOP = "👑 ئەندامێ د حەڤتیێ دا ژ هەمیان اکتیڤتر:"
    TODAY_STATS = "📊 ئەفروکە {} هندە نامە هاتن"
    
    # Admin Mesajları
    NOT_ADMIN = "⛔ تە دەستوری ئەمە نینە!"
    ADMIN_LIST = "👮 لیستا ئەدمینان:"


# ==================== VERİTABANI ====================
class Database:
    def __init__(self):
        self.users_file = 'users.json'
        self.messages_file = 'messages.json'
        self.penalties_file = 'penalties.json'
        self.admins_file = 'admins.json'  # Admin listesi
        self.load_data()
    
    def load_data(self):
        for file in [self.users_file, self.messages_file, self.penalties_file, self.admins_file]:
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False)
    
    def save_admins(self, admin_list):
        """Admin listesini kaydet"""
        with open(self.admins_file, 'w', encoding='utf-8') as f:
            json.dump(admin_list, f, ensure_ascii=False, indent=2)
    
    def get_admins(self):
        """Admin listesini getir"""
        with open(self.admins_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def is_admin(self, user_id):
        """Kullanıcı admin mi?"""
        admins = self.get_admins()
        return str(user_id) in admins
    
    def add_message(self, user_id, username, first_name):
        today = datetime.now().strftime("%Y-%m-%d")
        user_id_str = str(user_id)
        
        # Kullanıcıyı kaydet
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        users[user_id_str] = {
            'username': username or first_name,
            'first_name': first_name,
            'last_seen': datetime.now().isoformat()
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
                'last_message': datetime.now().isoformat()
            }
            
            with open(self.penalties_file, 'w', encoding='utf-8') as f:
                json.dump(penalties, f, ensure_ascii=False, indent=2)
    
    def update_penalties(self):
        """24 saat mesaj göndermeyenlere eksi ekle (adminler hariç)"""
        with open(self.penalties_file, 'r', encoding='utf-8') as f:
            penalties = json.load(f)
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        admins = self.get_admins()
        one_day_ago = datetime.now() - timedelta(days=1)
        
        for user_id, user_data in users.items():
            # Adminleri atla
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
        """3 eksiye ulaşanları getir (adminler hariç)"""
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
        """24 saat içinde mesaj göndermeyenler (adminler hariç)"""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        admins = self.get_admins()
        one_day_ago = datetime.now() - timedelta(days=1)
        inactive = []
        
        for user_id, user_data in users.items():
            if user_id in admins:
                continue
            last_seen = datetime.fromisoformat(user_data.get('last_seen', '2000-01-01'))
            if last_seen < one_day_ago:
                username = user_data.get('username', user_data.get('first_name', 'Bilinmiyor'))
                inactive.append(username)
        
        return inactive
    
    def get_top_users(self, hours):
        """Belirtilen saat diliminde en çok mesaj göndereni bul"""
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        since_date = (datetime.now() - timedelta(hours=hours)).date()
        
        user_counts = {}
        for date_str, daily_msgs in messages.items():
            msg_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if msg_date >= since_date:
                for user_id, count in daily_msgs.items():
                    user_counts[user_id] = user_counts.get(user_id, 0) + count
        
        if not user_counts:
            return None
        
        top_user_id = max(user_counts, key=user_counts.get)
        top_count = user_counts[top_user_id]
        
        user_data = users.get(top_user_id, {})
        username = user_data.get('username', user_data.get('first_name', 'Bilinmiyor'))
        
        return (username, top_count)


# ==================== ANA BOT ====================
class BadiniAnalizBot:
    def __init__(self, token):
        self.token = token
        self.db = Database()
        self.msgs = BadiniMessages()
    
    async def update_admins(self, context):
        """Gruptaki adminleri güncelle"""
        try:
            if not GROUP_ID:
                return
            
            # Grup üyelerini al
            admins = await context.bot.get_chat_administrators(GROUP_ID)
            
            admin_dict = {}
            for admin in admins:
                user = admin.user
                admin_dict[str(user.id)] = {
                    'username': user.username or user.first_name,
                    'first_name': user.first_name,
                    'is_owner': isinstance(admin, ChatMemberOwner)
                }
            
            # Adminleri kaydet
            self.db.save_admins(admin_dict)
            logging.info(f"✅ {len(admin_dict)} admin güncellendi")
            
        except Exception as e:
            logging.error(f"Admin güncelleme hatası: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start komutu - herkese açık"""
        await update.message.reply_text(
            f"👋 **{self.msgs.WELCOME}**\n\n"
            f"**{self.msgs.BOT_NAME}**\n\n"
            f"ℹ️ ئەز بوتێ تحلیلێ گروپێ مە\n"
            f"📊 داتایێن 24 سعەت و حەڤتیێ\n"
            f"⚠️ سیستمێ جزایێن بێدەنگیان"
        )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/admin komutu - admin listesi (sadece adminler)"""
        # Admin mi kontrol et
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        # Admin listesini göster
        admins = self.db.get_admins()
        msg = f"**{self.msgs.ADMIN_LIST}**\n\n"
        
        for admin_id, admin_data in admins.items():
            role = "👑" if admin_data.get('is_owner') else "👮"
            name = admin_data.get('username', admin_data.get('first_name', '?'))
            msg += f"{role} {name}\n"
        
        await update.message.reply_text(msg)
    
    async def force_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/force_report - manuel rapor (sadece adminler)"""
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        await update.message.reply_text("🚀 رەپورت هاتیە ئامادەکرن...")
        
        # Raporu gruba gönder
        await self.send_daily_report(context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gelen mesajları işle"""
        # Sadece gruplar
        if update.effective_chat.type not in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        if not user:
            return
        
        # Mesajı kaydet
        self.db.add_message(user.id, user.username, user.first_name)
    
    async def send_daily_report(self, context):
        """Günlük rapor gönder"""
        if not GROUP_ID:
            return
        
        # En çok mesaj gönderenler
        top_user_24h = self.db.get_top_users(24)
        top_user_12h = self.db.get_top_users(12)
        inactive = self.db.get_inactive_users_24h()
        
        msg = f"**📊 {self.msgs.REPORT_24H}**\n\n"
        
        # 24 saat en çok
        if top_user_24h:
            username, count = top_user_24h
            msg += f"**🏆 {self.msgs.TOP_MESSAGERS} (24h):**\n"
            msg += f"👑 {username} - {count} {self.msgs.MESSAGE}\n\n"
        
        # 12 saat en çok
        if top_user_12h:
            username, count = top_user_12h
            msg += f"**🥇 {self.msgs.TOP_MESSAGERS} (12h):**\n"
            msg += f"👑 {username} - {count} {self.msgs.MESSAGE}\n\n"
        
        # Pasifler
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
        
        # Haftanın en aktif üyesi
        top_weekly = self.db.get_top_users(168)
        
        msg = f"**📈 {self.msgs.REPORT_WEEKLY}**\n\n"
        
        if top_weekly:
            username, count = top_weekly
            msg += f"**👑 {self.msgs.WEEKLY_TOP}**\n"
            msg += f"**{username}** - {count} {self.msgs.MESSAGE}\n\n"
        
        # 3 eksiye ulaşanlar
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
        
        # 3 eksiye ulaşanları bildir
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
        """Admin listesini güncelle (her gün)"""
        await self.update_admins(context)
    
    def run(self):
        """Botu başlat"""
        application = Application.builder().token(self.token).build()
        
        # Komutlar (herkese açık)
        application.add_handler(CommandHandler("start", self.start_command))
        
        # Admin komutları (admin kontrolü içeride)
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CommandHandler("force_report", self.force_report_command))
        
        # Mesaj handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Bot başlarken adminleri güncelle
        async def init_admins(app):
            await self.update_admins(app)
        
        application.post_init = init_admins
        
        # Zamanlanmış görevler
        job_queue = application.job_queue
        
        if job_queue:
            # Her gün adminleri güncelle
            job_queue.run_daily(
                self.update_admins_job,
                time=datetime.time(hour=3, minute=0)  # Gece 3'te
            )
            
            # Her gün eksileri kontrol et
            job_queue.run_daily(
                self.check_penalties_job,
                time=datetime.time(hour=0, minute=30)  # Gece 12:30'da
            )
            
            # Her gün rapor gönder
            job_queue.run_daily(
                self.send_daily_report,
                time=datetime.time(hour=23, minute=59)  # Gece 23:59'da
            )
            
            # Her Pazar haftalık rapor
            job_queue.run_daily(
                self.send_weekly_report,
                time=datetime.time(hour=23, minute=59),
                days=(6,)  # Pazar
            )
        
        # Botu başlat
        print(f"🚀 {self.msgs.BOT_NAME} başladı...")
        print(f"📊 Grup ID: {GROUP_ID}")
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
