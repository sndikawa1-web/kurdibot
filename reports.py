# reports.py
import datetime
import schedule
import time
import threading
import pytz
from utils import BadiniTranslations, get_iraq_time, get_mention_html
from config import DAILY_REPORT_TIME

class ReportSystem:
    def __init__(self, bot, db, allowed_group_id):
        self.bot = bot
        self.db = db
        self.allowed_group_id = allowed_group_id
        self.translations = BadiniTranslations()
        self.start_scheduler()
    
    def start_scheduler(self):
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        # NOT: Railway UTC kullanır, Irak saati için UTC'ye çeviriyoruz
        # Irak = UTC + 3 saat
        
        # Günlük en aktif 5 kişi (Irak saati 03:00 için UTC 00:00)
        schedule.every().day.at("00:00").do(self.send_daily_top_users)
        
        # Günlük rapor (Irak saati 00:00 için UTC 21:00 - önceki gün)
        schedule.every().day.at("21:00").do(self.send_daily_report)
        
        # Haftalık rapor (Pazartesi Irak 00:05 için UTC 21:05 Pazar)
        schedule.every().monday.at("21:05").do(self.send_weekly_report)
        
        # 3 gün konuşmayanları kontrol et (her 6 saatte bir - Irak saatine göre ayarlı)
        # 03:00, 09:00, 15:00, 21:00 Irak için UTC: 00:00, 06:00, 12:00, 18:00
        schedule.every().day.at("00:00").do(self.check_inactive_3days)  # Irak 03:00
        schedule.every().day.at("06:00").do(self.check_inactive_3days)  # Irak 09:00
        schedule.every().day.at("12:00").do(self.check_inactive_3days)  # Irak 15:00
        schedule.every().day.at("18:00").do(self.check_inactive_3days)  # Irak 21:00
        
        # 24 saat konuşmayanları kontrol et (günde 2 kez - Irak 12:00 ve 00:00)
        schedule.every().day.at("09:00").do(self.check_inactive_24h)  # Irak 12:00
        schedule.every().day.at("21:00").do(self.check_inactive_24h)  # Irak 00:00 (gece yarısı)
        
        thread = threading.Thread(target=run_schedule, daemon=True)
        thread.start()
        print("✅ Zamanlanmış görevler başlatıldı")
        print("   📍 Irak saati için UTC ayarları yapıldı")
    
    def send_daily_top_users(self):
        """Günlük en aktif 5 kişiyi gönder (Irak saati 03:00)"""
        try:
            daily_top = self.db.get_daily_top_users(5)
            
            if not daily_top:
                return
            
            message = "ئەو کەسێن ئەفرو ژ هەمیا پتر نامە رێکرین\n\n"
            
            medals = ["🥇", "🥈", "🥉", "🏅", "🎖️"]
            
            for i, (user_id, msg_count) in enumerate(daily_top):
                if i >= 5:
                    break
                    
                # Kullanıcı bilgilerini al
                self.db.cursor.execute('SELECT username, first_name FROM users WHERE user_id = ?', (user_id,))
                user_data = self.db.cursor.fetchone()
                
                if user_data:
                    username, first_name = user_data
                    mention = get_mention_html(user_id, username, first_name)
                    message += f"{medals[i]} {mention} 🎉\n"
            
            message += "\nدەستخوش بەردەوامبن ب هاریکاریا وە گروپ دێ هەر اکتیڤ بت 🤝💯"
            
            self.bot.send_message(
                self.allowed_group_id,
                message,
                parse_mode='HTML'
            )
            print("✅ Günlük en aktif 5 kişi gönderildi")
            
        except Exception as e:
            print(f"❌ Günlük en aktif 5 kişi hatası: {e}")
    
    def send_daily_report(self):
        try:
            inactive_users = self.db.get_inactive_users_24h()
            report = self.translations.inactive_24h_report(inactive_users)
            
            self.bot.send_message(
                self.allowed_group_id,
                f"📊 RAPORA ROJANE\n\n{report}",
                parse_mode='HTML'
            )
            print("✅ Günlük rapor gönderildi")
        except Exception as e:
            print(f"❌ Günlük rapor hatası: {e}")
    
    def send_weekly_report(self):
        try:
            # Haftalık en aktif kullanıcılar
            week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            
            self.db.cursor.execute('''
                SELECT user_id, COUNT(*) as msg_count 
                FROM users 
                WHERE last_message_date > ? 
                GROUP BY user_id 
                ORDER BY msg_count DESC 
                LIMIT 5
            ''', (week_ago,))
            
            weekly_stats = self.db.cursor.fetchall()
            
            message = "📅 RAPORA HEFANE\n\n"
            
            if not weekly_stats:
                message += "ڤی هەفتەیی چالاکی نینە"
            else:
                for i, (user_id, msg_count) in enumerate(weekly_stats, 1):
                    user_data = self.db.get_user_stats(user_id)
                    if user_data:
                        username, first_name, xp, level, total_msgs, _ = user_data
                        mention = get_mention_html(user_id, username, first_name)
                        message += f"{i}. {mention} - {msg_count} نامە (Level {level})\n"
            
            self.bot.send_message(self.allowed_group_id, message, parse_mode='HTML')
            print("✅ Haftalık rapor gönderildi")
        except Exception as e:
            print(f"❌ Haftalık rapor hatası: {e}")
    
    def check_inactive_24h(self):
        """Günde 2 kez 24 saat konuşmayanları kontrol et (toplu olarak)"""
        try:
            inactive_users = self.db.get_inactive_users_24h()
            
            if not inactive_users:
                return
            
            # Toplu mesaj gönder (5'er 5'er)
            for i in range(0, len(inactive_users), 5):
                batch = inactive_users[i:i+5]
                
                message = "🔔 24 SAAT KONUŞMAYANLAR 🔔\n\n"
                
                for user in batch:
                    user_id, username, first_name = user
                    mention = get_mention_html(user_id, username, first_name)
                    message += f"• {mention}\n"
                
                message += "\nبەرێز ٢٤ کاتژمێر بورین تە هیچ نامەیە ڤرێنەکرە \n"
                message += "پێدفیە نامەکێ ڤرێکەی گروپی 🤝💕"
                
                self.bot.send_message(
                    self.allowed_group_id, 
                    message, 
                    parse_mode='HTML'
                )
                print(f"✅ 24h toplu uyarı gönderildi: {len(batch)} kişi")
                
                time.sleep(2)  # Rate limit koruması
                
        except Exception as e:
            print(f"❌ 24h kontrol hatası: {e}")
    
    def check_inactive_3days(self):
        """Günde 4 kez 3 gün konuşmayanları kontrol et (toplu olarak)"""
        try:
            inactive_users = self.db.get_inactive_users_3days()
            
            if not inactive_users:
                return
            
            # Toplu mesaj gönder (3'er 3'er)
            for i in range(0, len(inactive_users), 3):
                batch = inactive_users[i:i+3]
                
                message = "⚠️ 3 ROJ KONUŞMAYANLAR ⚠️\n\n"
                
                for user in batch:
                    user_id, username, first_name, last_date = user
                    mention = get_mention_html(user_id, username, first_name)
                    message += f"• {mention}\n"
                
                message += "\nئاگهداری ( سێ ٣ ) روژە تە نامە رێنەکری گروپی\n"
                message += "هیفیە نامەکێ ڤرێکە ئەگەر دێ هێیە دەرێخستن ❌🔕"
                
                self.bot.send_message(
                    self.allowed_group_id, 
                    message, 
                    parse_mode='HTML'
                )
                print(f"✅ 3 gün toplu uyarı gönderildi: {len(batch)} kişi")
                
                time.sleep(2)  # Rate limit koruması
                
        except Exception as e:
            print(f"❌ 3 gün kontrol hatası: {e}")
