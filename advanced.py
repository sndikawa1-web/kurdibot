# ==================== GELİŞMİŞ BOT (YENİ ÖZELLİKLER) ====================
import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from messages import BadiniMessages, AdvancedMessages, IRAQ_TZ
from database import Database

TOKEN = os.environ.get('BOT_TOKEN')
GROUP_ID = int(os.environ.get('GROUP_ID', 0))

logging.basicConfig(level=logging.INFO)

class AdvancedBot:
    def __init__(self, token):
        self.token = token
        self.db = Database()
        self.msgs = BadiniMessages()
        self.adv_msgs = AdvancedMessages()
    
    async def top10_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_users = self.db.get_all_users_message_counts_24h()
        
        if not all_users:
            await update.message.reply_text(f"📊 {self.adv_msgs.TOP10}\n\n{self.msgs.NO_MESSAGES}")
            return
        
        msg = f"📊 {self.adv_msgs.TOP10}\n\n"
        for i, (display_name, count, user_id) in enumerate(all_users[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            msg += f"{medal} {display_name} - {count} {self.msgs.MESSAGE}\n"
        
        await update.message.reply_text(msg)
    
    async def weekly_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_users = self.db.get_all_users_message_counts_24h()
        
        msg = f"📊 {self.adv_msgs.WEEKLY_RANKING}\n\n"
        if all_users:
            for i, (display_name, count, user_id) in enumerate(all_users[:10], 1):
                msg += f"{i}. {display_name} - {count} {self.msgs.MESSAGE}\n"
        else:
            msg += self.msgs.NO_MESSAGES
        
        await update.message.reply_text(msg)
    
    async def monthly_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = f"📊 {self.adv_msgs.MONTHLY_RANKING}\n\n"
        msg += "🔄 واهاتە... (Yakında)"
        await update.message.reply_text(msg)
    
    async def active_hours_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        top_hours = self.db.get_most_active_hours()
        
        msg = f"⏰ {self.adv_msgs.ACTIVE_HOURS}\n\n"
        for hour, count in top_hours:
            msg += f"🕐 {hour} - {count} {self.msgs.MESSAGE}\n"
        
        await update.message.reply_text(msg)
    
    async def badges_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = f"🏅 {self.adv_msgs.BADGE}\n\n"
        msg += f"• {self.adv_msgs.BADGE_7DAYS}\n"
        msg += f"• {self.adv_msgs.BADGE_500MSG}\n"
        msg += f"• {self.adv_msgs.BADGE_1000MSG}\n"
        msg += f"• {self.adv_msgs.BADGE_MOST_MSG}\n"
        msg += f"• {self.adv_msgs.BADGE_SPECIAL}\n"
        
        await update.message.reply_text(msg)
    
    async def level_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = f"📊 {self.adv_msgs.LEVEL}\n\n"
        msg += f"• Her mesaj = 10 XP\n"
        msg += f"• Her 200 XP = 1 Level\n"
        msg += f"• XP biriktir, level atla!\n"
        
        await update.message.reply_text(msg)
    
    async def reminder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = f"⏰ {self.adv_msgs.REMINDER_24H}\n\n"
        msg += "🔄 Yakında..."
        await update.message.reply_text(msg)
    
    async def records_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = f"🏆 {self.adv_msgs.GROUP_SCORE}\n\n"
        msg += "🔄 Yakında..."
        await update.message.reply_text(msg)
    
    async def myrank_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        msg = f"📊 {self.adv_msgs.MY_RANK}\n\n"
        msg += f"👤 @{username}\n"
        msg += "🔄 Yakında..."
        
        await update.message.reply_text(msg)
    
    async def mybadges_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = f"🏅 {self.adv_msgs.MY_BADGES}\n\n"
        msg += "🔄 Yakında..."
        await update.message.reply_text(msg)
    
    async def weekly_champ_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        all_users = self.db.get_all_users_message_counts_24h()
        
        if not all_users:
            await update.message.reply_text("🏆 هێشتا داتا نینە!")
            return
        
        champ = all_users[0]
        
        msg = f"👑 {self.adv_msgs.WEEKLY_CHAMP}\n\n"
        msg += f"🏆 {champ[0]}\n"
        msg += f"📊 {champ[1]} {self.msgs.MESSAGE}\n\n"
        msg += f"🎉 {self.adv_msgs.CONGRAT_CHAMP}"
        
        await update.message.reply_text(msg)
    
    async def quality_score_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = f"📊 {self.adv_msgs.GROUP_QUALITY}\n\n"
        msg += "🔄 Yakında..."
        await update.message.reply_text(msg)
    
    def run(self):
        application = Application.builder().token(self.token).build()
        
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
        
        print(f"🚀 Gelişmiş Bot başladı...")
        application.run_polling()

if __name__ == "__main__":
    if not TOKEN:
        print("❌ HATA: BOT_TOKEN bulunamadı!")
        exit(1)
    
    bot = AdvancedBot(TOKEN)
    bot.run()
