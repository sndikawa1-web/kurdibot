import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token'ı environment variable'dan al
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Ben çalışıyorum ✅")

# /test komutu
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Test başarılı! Bot aktif.")

def main():
    # Botu başlat
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutları ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    
    # Botu çalıştır
    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == '__main__':
    main()
