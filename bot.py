import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from googletrans import Translator

# Token'ı environment variable'dan al
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Çeviri yapıcı
translator = Translator()

# Loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Dil kodları
DILLER = {
    'ku': 'Kürtçe (Kurmanci)',
    'ckb': 'Kürtçe (Sorani)'
}

async def ceviri_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ /kr komutu çalışınca butonları göster """
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Lütfen çevrilecek mesajı YANITLA (reply) ve /kr yazın!")
        return
    
    orijinal_mesaj = update.message.reply_to_message.text
    
    if not orijinal_mesaj:
        await update.message.reply_text("❌ Bu mesaj çevrilemez (resim veya video olabilir)!")
        return
    
    context.user_data['cevrilecek_mesaj'] = orijinal_mesaj
    context.user_data['mesaj_sahibi'] = update.message.reply_to_message.from_user.first_name
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Kurmanci", callback_data='ku'),
            InlineKeyboardButton("📚 Sorani", callback_data='ckb')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔍 Çevrilecek mesaj:\n\"{orijinal_mesaj[:50]}...\"\n\n"
        f"Hangi lehçeye çevirelim?",
        reply_markup=reply_markup
    )

async def buton_tiklandi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Butona tıklanınca çeviriyi yap """
    
    query = update.callback_query
    await query.answer()
    
    secilen_dil = query.data
    dil_adi = DILLER[secilen_dil]
    
    orijinal_mesaj = context.user_data.get('cevrilecek_mesaj', '')
    mesaj_sahibi = context.user_data.get('mesaj_sahibi', 'Bir üye')
    
    try:
        ceviri = translator.translate(orijinal_mesaj, dest=secilen_dil)
        
        await query.edit_message_text(
            f"✅ **Çeviri Tamamlandı**\n\n"
            f"👤 **{mesaj_sahibi}** yazdı:\n"
            f"💬 {orijinal_mesaj}\n\n"
            f"📖 **{dil_adi}**:\n"
            f"🗣 {ceviri.text}"
        )
        
    except Exception as e:
        await query.edit_message_text(f"❌ Çeviri başarısız: {str(e)}")

def main():
    # Botu başlat
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutları ekle
    app.add_handler(CommandHandler("kr", ceviri_komutu))
    app.add_handler(CallbackQueryHandler(buton_tiklandi))
    
    # Botu çalıştır
    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == '__main__':
    main()
