# ==================== ANA BOT ====================
import os
import logging
import asyncio
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

from config import TOKEN, GROUP_ID, IRAQ_TZ
from messages import Messages
from database import Database
from levels import LevelSystem
from utils import format_time, split_message

# Loglama
logging.basicConfig(level=logging.INFO)

class BadiniBot:
    def __init__(self):
        self.db = Database()
        self.msgs = Messages()
        self.level_system = LevelSystem(self.db)
        self.first_run = True
        self.user_state = {}  # Kullanıcıların menü durumu
    
    async def check_group(self, update: Update):
        if update.effective_chat.type == 'private':
            await update.message.reply_text(self.msgs.PRIVATE_CHAT_ERROR)
            return False
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(self.msgs.WRONG_GROUP_ERROR)
            return False
        return True
    
    async def update_admins(self, context):
        try:
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
            
            self.db.save_admins(admin_dict)
            logging.info(f"✅ {len(admin_dict)} admin güncellendi")
            
        except Exception as e:
            logging.error(f"Admin güncelleme hatası: {e}")
    
    # ========== TOP MENU KOMUTU ==========
    async def top(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📋 /top - Ana menü"""
        if not await self.check_group(update):
            return
        
        user_id = update.effective_user.id
        
        menu_text = f"{self.msgs.TOP_MENU_TITLE}\n{self.msgs.TOP_MENU_OPTIONS}\n{self.msgs.TOP_MENU_PROMPT}"
        self.user_state[user_id] = "main_menu"
        
        await update.message.reply_text(menu_text)
    
    async def handle_menu_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menüden gelen seçimleri işle"""
        if update.effective_chat.id != GROUP_ID:
            return False
        
        user_id = update.effective_user.id
        
        if user_id not in self.user_state:
            return False
        
        text = update.message.text.strip()
        
        if not text.isdigit():
            await update.message.reply_text(self.msgs.TOP_MENU_INVALID)
            return True
        
        choice = int(text)
        
        if choice < 1 or choice > 11:
            await update.message.reply_text(self.msgs.TOP_MENU_INVALID)
            return True
        
        # Kullanıcı durumunu temizle
        del self.user_state[user_id]
        
        # Seçime göre işlem yap
        if choice == 1:  # Admin Raporu
            if self.db.is_admin(user_id):
                await self.rapor(update, context)
            else:
                await update.message.reply_text(self.msgs.NOT_ADMIN)
        
        elif choice == 2:  # Admin Güncelle
            if self.db.is_admin(user_id):
                await self.reload(update, context)
            else:
                await update.message.reply_text(self.msgs.NOT_ADMIN)
        
        elif choice == 3:  # Top 10 Messages
            await self.top10(update, context)
        
        elif choice == 4:  # Weekly Ranking
            await self.weekly(update, context)
        
        elif choice == 5:  # Monthly Ranking
            await self.monthly(update, context)
        
        elif choice == 6:  # Active Hours
            await self.active_hours(update, context)
        
        elif choice == 7:  # Group Quality
            await self.quality(update, context)
        
        elif choice == 8:  # Weekly Champion
            await self.weekly_champ(update, context)
        
        elif choice == 9:  # My Level
            await self.level(update, context)
        
        elif choice == 10:  # Level Ranking
            await self.level_ranking(update, context)
        
        elif choice == 11:  # 24h Passive
            await self.pasif(update, context)
        
        return True
    
    # ========== ESKİ KOMUTLAR (FONKSİYONLAR) ==========
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_group(update):
            return
        
        now = datetime.now(IRAQ_TZ)
        await update.message.reply_text(
            f"👋 {self.msgs.WELCOME}\n\n"
            f"{self.msgs.BOT_NAME}\n\n"
            f"📊 داتایێن 24 سعەت و حەڤتیێ\n"
            f"⚠️ سیستمێ جزایێن بێدەنگیان\n\n"
            f"📋 /top - مێنوی سەرەکی\n"
            f"⏰ کاتی عێراق: {now.strftime('%H:%M')}"
        )
    
    async def rapor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        await update.message.reply_text(self.msgs.REPORT_PREPARING)
        
        all_users = self.db.get_all_users_message_counts(24)
        inactive = self.db.get_inactive_users_24h()
        now = datetime.now(IRAQ_TZ)
        
        msg = f"📊 {self.msgs.REPORT_24H}\n\n"
        msg += f"⏰ کاتی عێراق: {format_time(now)}\n\n"
        
        if all_users:
            msg += f"📝 {self.msgs.MESSAGE_LIST}\n"
            for i, (display, count, _) in enumerate(all_users, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📌"
                msg += f"{medal} {display} - {count} {self.msgs.MESSAGE}\n"
            
            msg += f"\n📊 {self.msgs.TOTAL}: {len(all_users)} {self.msgs.MEMBER}\n\n"
        else:
            msg += f"{self.msgs.NO_MESSAGES}\n\n"
        
        if inactive:
            msg += f"💤 {self.msgs.INACTIVE_24H}\n"
            for username in inactive[:10]:
                msg += f"• {username}\n"
        
        await update.message.reply_text(msg)
    
    async def reload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        await update.message.reply_text(self.msgs.ADMIN_UPDATING)
        await self.update_admins(context)
        await update.message.reply_text(self.msgs.ADMIN_UPDATED)
    
    async def top10(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_users = self.db.get_all_users_message_counts(24)
        
        if not all_users:
            await update.message.reply_text(f"📊 {self.msgs.TOP10}\n\n{self.msgs.NO_MESSAGES}")
            return
        
        msg = f"📊 {self.msgs.TOP10}\n\n"
        for i, (display, count, _) in enumerate(all_users[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            msg += f"{medal} {display} - {count} {self.msgs.MESSAGE}\n"
        
        await update.message.reply_text(msg)
    
    async def weekly(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_users = self.db.get_all_users_message_counts(168)
        
        msg = f"📊 {self.msgs.WEEKLY_RANKING}\n\n"
        if all_users:
            for i, (display, count, _) in enumerate(all_users[:10], 1):
                msg += f"{i}. {display} - {count} {self.msgs.MESSAGE}\n"
        else:
            msg += self.msgs.NO_MESSAGES
        
        await update.message.reply_text(msg)
    
    async def monthly(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_users = self.db.get_all_users_message_counts(720)
        
        msg = f"📊 {self.msgs.MONTHLY_RANKING}\n\n"
        if all_users:
            for i, (display, count, _) in enumerate(all_users[:10], 1):
                msg += f"{i}. {display} - {count} {self.msgs.MESSAGE}\n"
        else:
            msg += self.msgs.NO_MESSAGES
        
        await update.message.reply_text(msg)
    
    async def active_hours(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        top_hours = self.db.get_most_active_hours()
        
        msg = f"⏰ {self.msgs.ACTIVE_HOURS}\n\n"
        for hour, count in top_hours:
            msg += f"🕐 {hour} - {count} {self.msgs.MESSAGE}\n"
        
        await update.message.reply_text(msg)
    
    async def level(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        
        user_data = self.level_system.get_user_data(user_id)
        
        if user_data:
            msg = f"📊 {self.msgs.MY_LEVEL}\n\n"
            msg += f"👤 @{username}\n"
            msg += f"📊 {self.msgs.LEVEL}: {user_data['level']}\n"
            msg += f"⚡️ XP: {user_data['xp']}\n"
            msg += f"💬 {self.msgs.MESSAGE}: {user_data['total_messages']}\n"
            
            next_level_xp = self.level_system.get_xp_for_level(user_data['level'] + 1)
            remaining = next_level_xp - user_data['xp']
            if remaining > 0:
                msg += f"📈 لیفلی دویە: {remaining} XP یێ مایە"
        else:
            msg = f"📊 {self.msgs.LEVEL} Sistemi\n\n"
            msg += f"• هر نامە = 10 XP\n"
            msg += f"• لیفل 1-15: هر 200 XP = 1 لیفل\n"
            msg += f"• لیفل 15-30: هر 300 XP = 1 لیفل\n"
            msg += f"• لیفل 30+: هر 500 XP = 1 لیفل\n\n"
            msg += f"👤 @{username} هێشتا دەست پێ نەکرایە!"
        
        await update.message.reply_text(msg)
    
    async def level_ranking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        top_users = self.level_system.get_top_users(10)
        
        if not top_users:
            await update.message.reply_text("🏆 هێشتا داتا نینە!")
            return
        
        msg = f"🏆 لیفلا پیلترین (Top 10 Level)\n\n"
        
        for i, (display_name, level, xp, messages) in enumerate(top_users, 1):
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            msg += f"{medal} {display_name} - لیفل {level} (XP: {xp})\n"
        
        await update.message.reply_text(msg)
    
    async def weekly_champ(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_users = self.db.get_all_users_message_counts(168)
        
        if not all_users:
            await update.message.reply_text("🏆 هێشتا داتا نینە!")
            return
        
        champ = all_users[0]
        
        msg = f"👑 {self.msgs.WEEKLY_CHAMP}\n\n"
        msg += f"🏆 {champ[0]}\n"
        msg += f"📊 {champ[1]} {self.msgs.MESSAGE}\n\n"
        msg += f"🎉 {self.msgs.CONGRAT_CHAMP}"
        
        await update.message.reply_text(msg)
    
    async def quality(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_users = self.db.get_all_users_message_counts(24)
        inactive = self.db.get_inactive_users_24h()
        
        total = len(all_users) + len(inactive)
        active_ratio = (len(all_users) / total * 100) if total > 0 else 0
        
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
        msg += f"⭐️ {self.msgs.SCORE}: {score}/100\n"
        msg += f"📌 {quality}"
        
        await update.message.reply_text(msg)
    
    async def pasif(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        inactive = self.db.get_inactive_users_24h()
        
        if not inactive:
            await update.message.reply_text(f"✅ تو هەمی ئەندامان د 24 سعەتێ دا نامە رێکرە!")
            return
        
        msg = f"{self.msgs.PASSIVE_LIST}\n\n"
        for username in inactive[:20]:
            msg += f"• {username}\n"
        
        await update.message.reply_text(msg)
    
    # ========== HATIRLATMA GÖREVİ ==========
    async def reminder_job(self, context):
        if not GROUP_ID:
            return
        
        reminder_24h, reminder_3d = self.db.get_users_for_reminder()
        
        if reminder_24h:
            for user_id, display in reminder_24h[:5]:
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=self.msgs.REMINDER_24H.format(display)
                )
                await asyncio.sleep(1)
        
        if reminder_3d:
            for user_id, display in reminder_3d[:5]:
                await context.bot.send_message(
                    chat_id=GROUP_ID,
                    text=self.msgs.REMINDER_3DAYS.format(display)
                )
                await asyncio.sleep(1)
    
    # ========== OTOMATİK RAPORLAR ==========
    async def send_daily_report(self, context):
        if not GROUP_ID:
            return
        
        all_users = self.db.get_all_users_message_counts(24)
        inactive = self.db.get_inactive_users_24h()
        now = datetime.now(IRAQ_TZ)
        
        msg = f"📊 {self.msgs.REPORT_24H}\n\n"
        msg += f"⏰ کاتی عێراق: {format_time(now)}\n\n"
        
        if all_users:
            msg += f"📝 {self.msgs.MESSAGE_LIST}\n"
            for i, (display, count, _) in enumerate(all_users[:15], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📌"
                msg += f"{medal} {display} - {count} {self.msgs.MESSAGE}\n"
            
            msg += f"\n📊 {self.msgs.TOTAL}: {len(all_users)} {self.msgs.MEMBER}\n\n"
        else:
            msg += f"{self.msgs.NO_MESSAGES}\n\n"
        
        if inactive:
            msg += f"💤 {self.msgs.INACTIVE_24H}\n"
            for username in inactive[:10]:
                msg += f"• {username}\n"
        
        await context.bot.send_message(chat_id=GROUP_ID, text=msg)
    
    async def send_weekly_report(self, context):
        if not GROUP_ID:
            return
        
        all_users = self.db.get_all_users_message_counts(168)
        now = datetime.now(IRAQ_TZ)
        
        msg = f"📈 {self.msgs.REPORT_WEEKLY}\n\n"
        msg += f"⏰ کاتی عێراق: {format_time(now)}\n\n"
        
        if all_users:
            msg += f"👑 {self.msgs.WEEKLY_TOP}\n"
            msg += f"{all_users[0][0]} - {all_users[0][1]} {self.msgs.MESSAGE}\n\n"
            
            msg += f"📝 لیستا 10 پێشەنگ:\n"
            for i, (display, count, _) in enumerate(all_users[:10], 1):
                msg += f"{i}. {display} - {count} {self.msgs.MESSAGE}\n"
        else:
            msg += self.msgs.NO_MESSAGES
        
        await context.bot.send_message(chat_id=GROUP_ID, text=msg)
    
    async def check_penalties_job(self, context):
        if not GROUP_ID:
            return
        
        self.db.update_penalties()
        penalties = self.db.get_users_with_3_penalties()
        
        if penalties:
            msg = f"⚠️ {self.msgs.PENALTY_3_LIST}\n\n"
            for user_id, display in penalties:
                msg += f"• {display}\n"
            
            msg += f"\n💡 {self.msgs.RESET_PENALTY}"
            
            await context.bot.send_message(chat_id=GROUP_ID, text=msg)
    
    # ========== MESAJ HANDLER ==========
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != GROUP_ID:
            return
        
        # Önce menü seçimi mi kontrol et
        if await self.handle_menu_selection(update, context):
            return  # Menü seçimi işlendi, normal mesaj işleme geçme
        
        user = update.effective_user
        if not user:
            return
        
        # Normal mesaj işleme
        self.db.save_user(user.id, user.username, user.first_name)
        self.db.add_message(user.id)
        self.db.reset_penalty(user.id)
        
        total = self.db.get_total_message_count(user.id)
        leveled_up, new_level = self.level_system.update_user(
            user.id, 
            user.username or user.first_name, 
            total
        )
        
        if leveled_up:
            emoji_id = self.level_system.get_level_emoji_id(new_level)
            display_name = f"@{user.username}" if user.username else user.first_name
            
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=self.msgs.LEVEL_UP.format(
                    f"<emoji id={emoji_id}>",
                    new_level,
                    f"<emoji id={emoji_id}>",
                    f"{display_name} {new_level}"
                ),
                parse_mode='HTML'
            )
    
    def run(self):
        app = Application.builder().token(TOKEN).build()
        
        # SADECE 2 KOMUT: /top ve /start
        app.add_handler(CommandHandler("top", self.top))
        app.add_handler(CommandHandler("start", self.start))
        
        # Mesaj handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Bot başlarken adminleri güncelle
        async def init_admins(app):
            await self.update_admins(app)
        
        app.post_init = init_admins
        
        # Zamanlanmış görevler
        job_queue = app.job_queue
        
        if job_queue:
            # Her gün admin güncelleme (03:00)
            job_queue.run_daily(
                self.update_admins,
                time=datetime.time(hour=3, minute=0, tzinfo=IRAQ_TZ)
            )
            
            # Her gün hatırlatma (10:00)
            job_queue.run_daily(
                self.reminder_job,
                time=datetime.time(hour=10, minute=0, tzinfo=IRAQ_TZ)
            )
            
            # Her gün ceza kontrolü (00:30)
            job_queue.run_daily(
                self.check_penalties_job,
                time=datetime.time(hour=0, minute=30, tzinfo=IRAQ_TZ)
            )
            
            # Her gün rapor (00:00)
            job_queue.run_daily(
                self.send_daily_report,
                time=datetime.time(hour=0, minute=0, tzinfo=IRAQ_TZ)
            )
            
            # Her Pazar haftalık rapor (00:00)
            job_queue.run_daily(
                self.send_weekly_report,
                time=datetime.time(hour=0, minute=0, tzinfo=IRAQ_TZ),
                days=(6,)
            )
        
        print(f"🚀 {self.msgs.BOT_NAME} başladı...")
        print(f"📋 Komutlar: /top (ana menü), /start")
        app.run_polling()


# ==================== BAŞLAT ====================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ HATA: BOT_TOKEN bulunamadı!")
        exit(1)
    
    bot = BadiniBot()
    bot.run()
