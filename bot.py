import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from googletrans import Translator

# Token
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Çeviri
translator = Translator()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot aktif - Sadece Sorani çeviri yapar")

# /kr komutu
async def ceviri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Yanıt var mı?
        if not update.message.reply_to_message:
            return
        
        # Mesajı al
        mesaj = update.message.reply_to_message.text
        if not mesaj:
            return
        
        # SADECE Sorani'ye çevir (ckb)
        ceviri = translator.translate(mesaj, dest='ckb')
        
        # SADECE çeviriyi gönder
        await update.message.reply_text(ceviri.text)
        
    except:
        pass  # Hata olursa sessiz ol

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kr", ceviri))
    app.run_polling()

if __name__ == '__main__':
    main()
