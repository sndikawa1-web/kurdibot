# reports.py
import datetime
import schedule
import time
import threading
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
        
        # Günlük rapor (gece 00:00)
        schedule.every().day.at("00:00").do(self.send_daily_report)
        
        # Haftalık rapor (Pazartesi 00:05)
        schedule.every().monday.at("00:05").do(self.send_weekly_report)
        
        # 3 gün konuşmayanları kontrol et (her 6 saatte bir)
        schedule.every(6).hours.do(self.check_inactive_3days)
        
        # 24 saat konuşmayanları kontrol et (günde 2 kez: 12:00 ve 00:00)
        schedule.every().day.at("12:00").do(self.check_inactive_24h)
        schedule.every().day.at("00:00").do(self.check_inactive_24h)
        
        thread = threading.Thread(target=run_schedule, daemon=True)
        thread.start()
        print("✅ Zamanlanmış görevler başlatıldı")
    
    def send_daily_report(self):
        try:
            inactive_users = self.db.get_inactive_users_24h()
            report = self.translations.inactive_24h_report(inactive_users)
            
            self.bot.send_message(
                self.allowed_group_id,
                f"📊 **RAPORA ROJANE**\n\n{report}",
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
            
            message = "📅 **RAPORA HEFANE**\n\n"
            
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
                
                message = "🔔 **24 SAAT KONUŞMAYANLAR** 🔔\n\n"
                
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
        """Her 6 saatte bir 3 gün konuşmayanları kontrol et (toplu olarak)"""
        try:
            inactive_users = self.db.get_inactive_users_3days()
            
            if not inactive_users:
                return
            
            # Toplu mesaj gönder (3'er 3'er)
            for i in range(0, len(inactive_users), 3):
                batch = inactive_users[i:i+3]
                
                message = "⚠️ **3 Roj Konuşmayanlar** ⚠️\n\n"
                
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
