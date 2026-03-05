# ==================== ANA BOT (TEMEL ÖZELLİKLER) ====================
import os
import logging
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

from messages import BadiniMessages, IRAQ_TZ
from database import Database

TOKEN = os.environ.get('BOT_TOKEN')
GROUP_ID = int(os.environ.get('GROUP_ID', 0))

logging.basicConfig(level=logging.INFO)

class MainBot:
    def __init__(self, token):
        self.token = token
        self.db = Database()
        self.msgs = BadiniMessages()
        self.first_run = True
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type == 'private':
            await update.message.reply_text(self.msgs.PRIVATE_CHAT_ERROR)
            return
        
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(self.msgs.WRONG_GROUP_ERROR)
            return
        
        now = datetime.now(IRAQ_TZ)
        await update.message.reply_text(
            f"👋 {self.msgs.WELCOME}\n\n"
            f"{self.msgs.BOT_NAME}\n\n"
            f"📊 داتایێن 24 سعەت و حەڤتیێ\n"
            f"⚠️ سیستمێ جزایێن بێدەنگیان\n\n"
            f"📋 /rapor - {self.msgs.REPORT}\n"
            f"🔄 /reload - {self.msgs.RELOAD}\n"
            f"📊 /top10 - توپ 10\n"
            f"📈 /haftalik - حەڤتیانە\n"
            f"📅 /aylik - هەیفانە\n"
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
        if update.effective_chat.type == 'private':
            await update.message.reply_text(self.msgs.PRIVATE_CHAT_ERROR)
            return
        
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(self.msgs.WRONG_GROUP_ERROR)
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
        if update.effective_chat.type == 'private':
            await update.message.reply_text(self.msgs.PRIVATE_CHAT_ERROR)
            return
        
        if update.effective_chat.id != GROUP_ID:
            await update.message.reply_text(self.msgs.WRONG_GROUP_ERROR)
            return
        
        if not self.db.is_admin(update.effective_user.id):
            await update.message.reply_text(self.msgs.NOT_ADMIN)
            return
        
        await update.message.reply_text(self.msgs.ADMIN_UPDATING)
        # Admin güncelleme kodu
        await update.message.reply_text(self.msgs.ADMIN_UPDATED)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != GROUP_ID:
            return
        
        user = update.effective_user
        if not user:
            return
        
        self.db.add_message(user.id, user.username, user.first_name)
    
    def run(self):
        application = Application.builder().token(self.token).build()
        
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("rapor", self.rapor_command))
        application.add_handler(CommandHandler("reload", self.reload_command))
        
        # Gelişmiş komutlar advanced.py'den gelecek
        
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print(f"🚀 {self.msgs.BOT_NAME} başladı...")
        application.run_polling()

if __name__ == "__main__":
    if not TOKEN:
        print("❌ HATA: BOT_TOKEN bulunamadı!")
        exit(1)
    
    bot = MainBot(TOKEN)
    bot.run()
