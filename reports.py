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
        
        # 24 saat konuşmayanları kontrol et (her saat başı)
        schedule.every().hour.do(self.check_inactive_24h)
        
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
                        name = f"@{username}" if username else first_name
                        message += f"{i}. {name} - {msg_count} نامە (Level {level})\n"
            
            self.bot.send_message(self.allowed_group_id, message)
            print("✅ Haftalık rapor gönderildi")
        except Exception as e:
            print(f"❌ Haftalık rapor hatası: {e}")
    
    def check_inactive_24h(self):
        """Her saat başı 24 saat konuşmayanları kontrol et"""
        try:
            inactive_users = self.db.get_inactive_users_24h()
            
            for user in inactive_users[:5]:  # Çok fazla mesaj göndermemek için
                user_id, username, first_name = user
                name = f"@{username}" if username else first_name
                
                # YENİ 24 saat uyarı mesajı
                warn_msg = f"24h🔔{name}🔔\n"
                warn_msg += "بەرێز ٢٤ کاتژمێر بورین تە هیچ نامەیە ڤرێنەکرە \n"
                warn_msg += "پێدفیە نامەکێ ڤرێکەی گروپی 🤝💕"
                
                self.bot.send_message(self.allowed_group_id, warn_msg)
                print(f"✅ 24h uyarı gönderildi: {name}")
                
                time.sleep(2)  # Rate limit koruması
                
        except Exception as e:
            print(f"❌ 24h kontrol hatası: {e}")
    
    def check_inactive_3days(self):
        """Her 6 saatte bir 3 gün konuşmayanları kontrol et"""
        try:
            inactive_users = self.db.get_inactive_users_3days()
            
            for user in inactive_users[:3]:  # Çok fazla mesaj göndermemek için
                user_id, username, first_name, last_date = user
                name = f"@{username}" if username else first_name
                
                # YENİ 3 gün uyarı mesajı
                warn_msg = f"🔔{name}🔔\n"
                warn_msg += "ئاگهداری ( سێ ٣ ) روژە تە نامە رێنەکری گروپی هیفیە نامەکێ ڤرێکە ئەگەر دێ هێیە دەرێخستن ❌🔕"
                
                self.bot.send_message(self.allowed_group_id, warn_msg)
                print(f"✅ 3 gün uyarı gönderildi: {name}")
                
                time.sleep(2)  # Rate limit koruması
                
        except Exception as e:
            print(f"❌ 3 gün kontrol hatası: {e}")
