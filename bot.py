import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from googletrans import Translator

# Token'ı environment variable'dan al
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Çeviri yapıcı
translator = Translator()

# Loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇹🇷 ➡️ 🇰🇷 Türkçe-Kürtçe Çeviri Botu\n\n"
        "Kullanım: Bir mesajı yanıtlayın (reply) ve /kr yazın"
    )

# /kr komutu
async def ceviri_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Önce bir cevap verelim - test için
    await update.message.reply_text("Komut alındı, işleniyor...")
    
    # Mesajın yanıt olup olmadığını kontrol et
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Lütfen çevrilecek mesajı YANITLA (reply) ve /kr yazın!")
        return
    
    # Yanıtlanan mesajı al
    orijinal_mesaj = update.message.reply_to_message.text
    
    if not orijinal_mesaj:
        await update.message.reply_text("❌ Bu mesaj çevrilemez!")
        return
    
    # Mesajı geçici olarak kaydet
    context.user_data['cevrilecek_mesaj'] = orijinal_mesaj
    context.user_data['mesaj_sahibi'] = update.message.reply_to_message.from_user.first_name
    
    # Butonları oluştur
    keyboard = [
        [
            InlineKeyboardButton("📝 Kurmanci", callback_data='ku'),
            InlineKeyboardButton("📚 Sorani", callback_data='ckb')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔍 Hangi lehçeye çevirelim?",
        reply_markup=reply_markup
    )

# Butona tıklanınca
async def buton_tiklandi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Hangi buton tıklandı?
    secilen_dil = query.data
    dil_adi = "Kurmanci" if secilen_dil == 'ku' else "Sorani"
    
    # Kaydedilmiş mesajı al
    orijinal_mesaj = context.user_data.get('cevrilecek_mesaj', '')
    mesaj_sahibi = context.user_data.get('mesaj_sahibi', 'Bir üye')
    
    try:
        # Çeviriyi yap
        ceviri = translator.translate(orijinal_mesaj, dest=secilen_dil)
        
        # Sonucu gönder - buton mesajını düzenle
        await query.edit_message_text(
            f"👤 **{mesaj_sahibi}**: {orijinal_mesaj}\n\n"
            f"📖 **{dil_adi}**: {ceviri.text}"
        )
        
    except Exception as e:
        await query.edit_message_text(f"❌ Çeviri başarısız: Hata: {str(e)}")

def main():
    # Botu başlat
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komutları ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kr", ceviri_komutu))
    app.add_handler(CallbackQueryHandler(buton_tiklandi))
    
    # Botu çalıştır
    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == '__main__':
    main()
