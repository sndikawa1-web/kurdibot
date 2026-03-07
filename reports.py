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
        
        schedule.every().day.at("00:00").do(self.send_daily_report)
        schedule.every().monday.at("00:05").do(self.send_weekly_report)
        schedule.every(6).hours.do(self.check_inactive_3days)
        
        thread = threading.Thread(target=run_schedule, daemon=True)
        thread.start()
    
    def send_daily_report(self):
        try:
            inactive_users = self.db.get_inactive_users_24h()
            report = self.translations.inactive_24h_report(inactive_users, len(inactive_users))
            
            self.bot.send_message(
                self.allowed_group_id,
                report,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Rapora rojane hata: {e}")
    
    def send_weekly_report(self):
        try:
            weekly_stats = self.db.get_weekly_stats()
            
            detailed_stats = []
            for user_id, msg_count in weekly_stats:
                user_data = self.db.get_user_stats(user_id)
                if user_data:
                    username, first_name, xp, level, total_msgs, _ = user_data
                    detailed_stats.append((user_id, username, first_name, msg_count, level))
            
            message = self.translations.weekly_report(detailed_stats)
            
            self.bot.send_message(
                self.allowed_group_id,
                message,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Rapora heftane hata: {e}")
    
    def check_inactive_3days(self):
        try:
            inactive_users = self.db.get_inactive_users_3days()
            
            for user in inactive_users[:5]:
                user_id, username, first_name, last_date = user
                
                if username:
                    invite_msg = self.translations.invite_message(username=username)
                else:
                    invite_msg = self.translations.invite_message(first_name=first_name)
                
                self.bot.send_message(
                    self.allowed_group_id,
                    invite_msg,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"3 roj kontrol hata: {e}")
