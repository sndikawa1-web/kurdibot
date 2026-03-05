import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from googletrans import Translator

# Token'ı al
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Çeviri yapıcı
translator = Translator()

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Merhaba! Ben çeviri botuyum.\n\n"
        "Kullanım: Bir mesajı yanıtla (reply) ve /kr yaz"
    )

# /kr komutu
async def ceviri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Yanıtlanan mesaj var mı?
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Bir mesajı yanıtla ve /kr yaz!")
        return
    
    # Mesajı al
    mesaj = update.message.reply_to_message.text
    
    if not mesaj:
        await update.message.reply_text("❌ Bu mesaj çevrilemez!")
        return
    
    try:
        # Çeviriyi yap (Kürtçe'ye - otomatik Kurmanci)
        ceviri = translator.translate(mesaj, dest='ku')
        
        # Sadece çeviriyi gönder
        await update.message.reply_text(f"📖 {ceviri.text}")
        
    except Exception as e:
        await update.message.reply_text("❌ Çeviri başarısız")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kr", ceviri))
    
    app.run_polling()

if __name__ == '__main__':
    main()
