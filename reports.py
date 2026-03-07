# reports.py
import datetime
import schedule
import time
import threading
from utils import BadiniTranslations, get_iraq_time
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
        
        thread = threading.Thread(target=run_schedule, daemon=True)
        thread.start()
        print("✅ Zamanlanmış görevler başlatıldı")
    
    def send_daily_report(self):
        try:
            inactive_users = self.db.get_inactive_users_24h()
            report = self.translations.inactive_24h_report(inactive_users)
            
            self.bot.send_message(
                self.allowed_group_id,
                f"📊 **RAPORA ROJANE**\n\n{report}"
            )
            print("✅ Günlük rapor gönderildi")
        except Exception as e:
            print(f"❌ Günlük rapor hatası: {e}")
    
    def send_weekly_report(self):
        try:
            weekly_stats = self.db.get_weekly_stats()
            
            message = "📅 **RAPORA HEFANE**\n\n"
            
            if not weekly_stats:
                message += "ڤی هەفتەیی چالاکی نینە"
            else:
                for i, (user_id, msg_count) in enumerate(weekly_stats[:5], 1):
                    user_data = self.db.get_user_stats(user_id)
                    if user_data:
                        username, first_name, xp, level, total_msgs, _ = user_data
                        name = f"@{username}" if username else first_name
                        message += f"{i}. {name} - {msg_count} نامە (Level {level})\n"
            
            self.bot.send_message(self.allowed_group_id, message)
            print("✅ Haftalık rapor gönderildi")
        except Exception as e:
            print(f"❌ Haftalık rapor hatası: {e}")
    
    def check_inactive_3days(self):
        try:
            # 3 gün konuşmayanları kontrol et
            three_days_ago = (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat()
            
            self.db.cursor.execute('''
                SELECT user_id, username, first_name FROM users 
                WHERE last_message_date < ? OR last_message_date IS NULL
            ''', (three_days_ago,))
            
            inactive_users = self.db.cursor.fetchall()
            
            for user in inactive_users[:3]:  # Çok fazla mesaj göndermemek için
                user_id, username, first_name = user
                name = f"@{username}" if username else first_name
                
                invite_msg = f"🔔 {name}, 3 روژە تە نە ئاخفتنی! ها دە گروپ بە چالاک بە! 🗣️"
                
                self.bot.send_message(self.allowed_group_id, invite_msg)
                print(f"✅ Davet gönderildi: {name}")
                
                time.sleep(2)  # Rate limit koruması
                
        except Exception as e:
            print(f"❌ 3 gün kontrol hatası: {e}")
