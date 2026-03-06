# ==================== ANA BOT ====================
import os
import sys
import json
import logging
import asyncio
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackQueryHandler, ContextTypes

from config import TOKEN, GROUP_ID, IRAQ_TZ
from messages import Messages
from database import Database
from levels import LevelSystem
from utils import format_time, split_message

# Loglama
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BadiniBot:
    def __init__(self):
        self.db = Database()
        self.msgs = Messages()
        self.level_system = LevelSystem(self.db)
        self.first_run = True
        
        # YENİ LEVEL SİSTEMİ
        self.new_levels_file = 'new_levels.json'
        self.init_new_levels()
        logger.info("✅ Bot başlatılıyor...")
    
    def init_new_levels(self):
        """Yeni level dosyasını oluştur"""
        if not os.path.exists(self.new_levels_file):
            with open(self.new_levels_file, 'w') as f:
                json.dump({}, f)
    
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
            logger.info(f"✅ {len(admin_dict)} admin güncellendi")
            
        except Exception as e:
            logger.error(f"Admin güncelleme hatası: {e}")
    
    # ========== YENİ LEVEL SİSTEMİ ==========
    async def check_new_level(self, user_id, username, first_name, update, context):
        """YENİ level sistemi - her levelde 10 mesaj artar"""
        
        # Dosyayı oku
        with open(self.new_levels_file, 'r') as f:
            users = json.load(f)
        
        user_id_str = str(user_id)
        
        # İlk kez kayıt
        if user_id_str not in users:
            users[user_id_str] = {
                'username': username,
                'first_name': first_name,
                'messages': 0,
                'level': 1
            }
        
        # Mesaj sayısını artır
        users[user_id_str]['messages'] += 1
        message_count = users[user_id_str]['messages']
        current_level = users[user_id_str]['level']
        
        # Bu level için gereken mesaj sayısı: (current_level × 10) + 10
        required_messages = (current_level * 10) + 10
        
        # Level atlama kontrolü
        if message_count >= required_messages:
            # Yeni level
            new_level = current_level + 1
            users[user_id_str]['level'] = new_level
            users[user_id_str]['messages'] = message_count - required_messages
            
            # Kullanıcı adı yoksa ismini kullan
            if username:
                display_name = f"@{username}"
            else:
                display_name = first_name
            
            # Emoji seç (level'e göre)
            emoji_id = self.level_system.get_level_emoji_id(new_level)
            
            # BİLDİRİM GÖNDER (Badini Kürtçesi)
            next_required = (new_level * 10) + 10
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=f"{emoji_id} دەستخوش بویە لیفل {new_level} {emoji_id}\n📊 بۆ لیفلی دویە {next_required} نامە پێویستە"
            )
        
        # Kaydet
        with open(self.new_levels_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    async def test_new_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📊 /newlevel - Tüm kullanıcıların level sıralaması"""
        if not await self.check_group(update):
            return
        
        # Dosyayı oku
        with open(self.new_levels_file, 'r') as f:
            users = json.load(f)
        
        if not users:
            await update.message.reply_text("❌ هێشتا داتا نینە!")
            return
        
        # Kullanıcıları level'e göre sırala (yüksekten düşüğe)
        sorted_users = sorted(users.items(), key=lambda x: x[1]['level'], reverse=True)
        
        msg = "📊 **لیستا لیفلا (Level Sıralaması)**\n\n"
        
        for i, (user_id, data) in enumerate(sorted_users[:15], 1):  # İlk 15 kişi
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            # Kullanıcı adı yoksa ismini göster
            if data['username']:
                display_name = f"@{data['username']}"
            else:
                display_name = data['first_name']
            
            # Mevcut level için gereken mesaj
            current_level = data['level']
            required = (current_level * 10) + 10
            progress = data['messages']
            
            msg += f"{medal} {display_name} - لیفل {current_level} ({progress}/{required} نامە)\n"
        
        await update.message.reply_text(msg)
    
    # ========== BUTONLU MENÜ ==========
    async def top(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """📋 /top - Butonlu ana menü"""
        if not await self.check_group(update):
            return
        
        keyboard = [
            [
                InlineKeyboardButton("📋 rapor", callback_data="rapor"),
                InlineKeyboardButton("🔄 reload", callback_data="reload")
            ],
            [
                InlineKeyboardButton("📊 top10", callback_data="top10"),
                InlineKeyboardButton("📈 week", callback_data="week")
            ],
            [
                InlineKeyboardButton("📅 mont", callback_data="mont"),
                InlineKeyboardButton("⏰ saat", callback_data="saat")
            ],
            [
                InlineKeyboardButton("⭐️ kalite", callback_data="kalite"),
                InlineKeyboardButton("👑 top7", callback_data="top7")
            ],
            [
                InlineKeyboardButton("👤 me", callback_data="me"),
                InlineKeyboardButton("🏆 level", callback_data="level")
            ],
            [
                InlineKeyboardButton("💤 24h", callback_data="24h"),
                InlineKeyboardButton("📊 لیفلا", callback_data="newlevel")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 **مێنو**\n\nکلیکە ل سەر یەکێک ژ دوکمەکان:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Butonlara tıklanınca çalışır"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        command = query.data
        
        if command == "rapor":
            if self.db.is_admin(user_id):
                await self.rapor_callback(query, context)
            else:
                await query.edit_message_text(self.msgs.NOT_ADMIN)
        
        elif command == "reload":
            if self.db.is_admin(user_id):
                await self.reload_callback(query, context)
            else:
                await query.edit_message_text(self.msgs.NOT_ADMIN)
        
        elif command == "top10":
            await self.top10_callback(query, context)
        
        elif command == "week":
            await self.weekly_callback(query, context)
        
        elif command == "mont":
            await self.monthly_callback(query, context)
        
        elif command == "saat":
            await self.active_hours_callback(query, context)
        
        elif command == "kalite":
            await self.quality_callback(query, context)
        
        elif command == "top7":
            await self.weekly_champ_callback(query, context)
        
        elif command == "me":
            await self.level_callback(query, context)
        
        elif command == "level":
            await self.level_ranking_callback(query, context)
        
        elif command == "24h":
            await self.pasif_callback(query, context)
        
        elif command == "newlevel":
            await self.test_new_level_callback(query, context)
    
    async def test_new_level_callback(self, query, context):
        """Buton için newlevel callback'i"""
        with open(self.new_levels_file, 'r') as f:
            users = json.load(f)
        
        if not users:
            await query.edit_message_text("❌ هێشتا داتا نینە!")
            return
        
        sorted_users = sorted(users.items(), key=lambda x: x[1]['level'], reverse=True)
        
        msg = "📊 **لیستا لیفلا (Level Sıralaması)**\n\n"
        
        for i, (user_id, data) in enumerate(sorted_users[:15], 1):
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            if data['username']:
                display_name = f"@{data['username']}"
            else:
                display_name = data['first_name']
            
            current_level = data['level']
            required = (current_level * 10) + 10
            progress = data['messages']
            
            msg += f"{medal} {display_name} - لیفل {current_level} ({progress}/{required} نامە)\n"
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    # ========== CALLBACK FONKSİYONLARI ==========
    async def rapor_callback(self, query, context):
        await query.edit_message_text(self.msgs.REPORT_PREPARING)
        
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
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def reload_callback(self, query, context):
        await query.edit_message_text(self.msgs.ADMIN_UPDATING)
        await self.update_admins(context)
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(self.msgs.ADMIN_UPDATED, reply_markup=reply_markup)
    
    async def top10_callback(self, query, context):
        all_users = self.db.get_all_users_message_counts(24)
        
        if not all_users:
            msg = f"📊 {self.msgs.TOP10}\n\n{self.msgs.NO_MESSAGES}"
        else:
            msg = f"📊 {self.msgs.TOP10}\n\n"
            for i, (display, count, _) in enumerate(all_users[:10], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                msg += f"{medal} {display} - {count} {self.msgs.MESSAGE}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def weekly_callback(self, query, context):
        all_users = self.db.get_all_users_message_counts(168)
        
        msg = f"📊 {self.msgs.WEEKLY_RANKING}\n\n"
        if all_users:
            for i, (display, count, _) in enumerate(all_users[:10], 1):
                msg += f"{i}. {display} - {count} {self.msgs.MESSAGE}\n"
        else:
            msg += self.msgs.NO_MESSAGES
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def monthly_callback(self, query, context):
        all_users = self.db.get_all_users_message_counts(720)
        
        msg = f"📊 {self.msgs.MONTHLY_RANKING}\n\n"
        if all_users:
            for i, (display, count, _) in enumerate(all_users[:10], 1):
                msg += f"{i}. {display} - {count} {self.msgs.MESSAGE}\n"
        else:
            msg += self.msgs.NO_MESSAGES
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def active_hours_callback(self, query, context):
        top_hours = self.db.get_most_active_hours()
        
        msg = f"⏰ {self.msgs.ACTIVE_HOURS}\n\n"
        for hour, count in top_hours:
            msg += f"🕐 {hour} - {count} {self.msgs.MESSAGE}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def quality_callback(self, query, context):
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
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def weekly_champ_callback(self, query, context):
        all_users = self.db.get_all_users_message_counts(168)
        
        if not all_users:
            msg = "🏆 هێشتا داتا نینە!"
        else:
            champ = all_users[0]
            msg = f"👑 {self.msgs.WEEKLY_CHAMP}\n\n"
            msg += f"🏆 {champ[0]}\n"
            msg += f"📊 {champ[1]} {self.msgs.MESSAGE}\n\n"
            msg += f"🎉 {self.msgs.CONGRAT_CHAMP}"
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def level_callback(self, query, context):
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        
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
            msg = f"📊 {self.msgs.MY_LEVEL}\n\n"
            msg += f"👤 @{username}\n"
            msg += "هێشتا داتا نینە!"
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def level_ranking_callback(self, query, context):
        top_users = self.level_system.get_top_users(10)
        
        if not top_users:
            msg = "🏆 هێشتا داتا نینە!"
        else:
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
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def pasif_callback(self, query, context):
        inactive = self.db.get_inactive_users_24h()
        
        if not inactive:
            msg = f"✅ تو هەمی ئەندامان د 24 سعەتێ دا نامە رێکرە!"
        else:
            msg = f"{self.msgs.PASSIVE_LIST}\n\n"
            for username in inactive[:20]:
                msg += f"• {username}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 مێنو", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(msg, reply_markup=reply_markup)
    
    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menüye geri dön"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [
                InlineKeyboardButton("📋 rapor", callback_data="rapor"),
                InlineKeyboardButton("🔄 reload", callback_data="reload")
            ],
            [
                InlineKeyboardButton("📊 top10", callback_data="top10"),
                InlineKeyboardButton("📈 week", callback_data="week")
            ],
            [
                InlineKeyboardButton("📅 mont", callback_data="mont"),
                InlineKeyboardButton("⏰ saat", callback_data="saat")
            ],
            [
                InlineKeyboardButton("⭐️ kalite", callback_data="kalite"),
                InlineKeyboardButton("👑 top7", callback_data="top7")
            ],
            [
                InlineKeyboardButton("👤 me", callback_data="me"),
                InlineKeyboardButton("🏆 level", callback_data="level")
            ],
            [
                InlineKeyboardButton("💤 24h", callback_data="24h"),
                InlineKeyboardButton("📊 لیفلا", callback_data="newlevel")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📋 **مێنو**\n\nکلیکە ل سەر یەکێک ژ دوکمەکان:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ========== DİĞER KOMUTLAR ==========
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
            f"📊 /newlevel - لیستا لیفلا\n"
            f"⏰ کاتی عێراق: {now.strftime('%H:%M')}"
        )
    
    async def debug(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🔧 /debug - Sistem bilgileri"""
        if not await self.check_group(update):
            return
        
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        
        total = self.db.get_total_message_count(user_id)
        xp = total * 10
        level = self.level_system.calculate_level(xp)
        
        levels_exist = os.path.exists('levels.json')
        
        msg = f"🔧 **DEBUG BİLGİLERİ**\n\n"
        msg += f"👤 @{username}\n"
        msg += f"📊 Toplam mesaj: {total}\n"
        msg += f"⚡️ XP: {xp}\n"
        msg += f"📈 Hesaplanan Level: {level}\n"
        msg += f"📁 levels.json: {'✅ VAR' if levels_exist else '❌ YOK'}\n"
        
        if levels_exist:
            try:
                with open('levels.json', 'r') as f:
                    data = json.load(f)
                    user_data = data.get(str(user_id), 'KAYIT YOK')
                msg += f"👤 Kayıtlı: {user_data}"
            except:
                msg += f"❌ Okuma hatası"
        
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
        
        user = update.effective_user
        if not user:
            return
        
        # Mevcut sistem (eski level sistemi)
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
            level_message = f"{emoji_id} دەستخوش بویە لیفل {new_level} {emoji_id}\n\n{display_name}"
            await context.bot.send_message(
                chat_id=GROUP_ID,
                text=level_message,
                parse_mode='HTML'
            )
        
        # YENİ LEVEL SİSTEMİ (her levelde bildirimli)
        await self.check_new_level(user.id, user.username, user.first_name, update, context)
    
    def run(self):
        app = Application.builder().token(TOKEN).build()
        
        # Komutlar
        app.add_handler(CommandHandler("top", self.top))
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("debug", self.debug))
        app.add_handler(CommandHandler("newlevel", self.test_new_level))
        
        # Buton handler
        app.add_handler(CallbackQueryHandler(self.button_handler, pattern="^(rapor|reload|top10|week|mont|saat|kalite|top7|me|level|24h|newlevel)$"))
        app.add_handler(CallbackQueryHandler(self.back_to_menu, pattern="^back_to_menu$"))
        
        # Mesaj handler
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Bot başlarken adminleri güncelle
        async def init_admins(app):
            await self.update_admins(app)
        
        app.post_init = init_admins
        
        # Zamanlanmış görevler
        job_queue = app.job_queue
        
        if job_queue:
            job_queue.run_daily(
                self.update_admins,
                time=datetime.time(hour=3, minute=0, tzinfo=IRAQ_TZ)
            )
            
            job_queue.run_daily(
                self.reminder_job,
                time=datetime.time(hour=10, minute=0, tzinfo=IRAQ_TZ)
            )
            
            job_queue.run_daily(
                self.check_penalties_job,
                time=datetime.time(hour=0, minute=30, tzinfo=IRAQ_TZ)
            )
            
            job_queue.run_daily(
                self.send_daily_report,
                time=datetime.time(hour=0, minute=0, tzinfo=IRAQ_TZ)
            )
            
            job_queue.run_daily(
                self.send_weekly_report,
                time=datetime.time(hour=0, minute=0, tzinfo=IRAQ_TZ),
                days=(6,)
            )
        
        logger.info(f"🚀 {self.msgs.BOT_NAME} başladı...")
        logger.info(f"📋 Butonlu menü aktif: /top")
        logger.info(f"📊 Yeni level sistemi: Her levelde +10 mesaj artar, her levelde bildirim")
        app.run_polling()


# ==================== BAŞLAT ====================
if __name__ == "__main__":
    if not TOKEN:
        logger.error("❌ HATA: BOT_TOKEN bulunamadı!")
        exit(1)
    
    bot = BadiniBot()
    bot.run()
