# ==================== VERİTABANI ====================
import json
import os
from datetime import datetime, timedelta
from config import IRAQ_TZ

class Database:
    def __init__(self):
        self.users_file = 'users.json'
        self.messages_file = 'messages.json'
        self.penalties_file = 'penalties.json'
        self.admins_file = 'admins.json'
        self.levels_file = 'levels.json'
        self.records_file = 'records.json'
        self.hourly_file = 'hourly_stats.json'
        self.load_data()
    
    def load_data(self):
        files = [self.users_file, self.messages_file, self.penalties_file, 
                 self.admins_file, self.levels_file, self.records_file, self.hourly_file]
        for file in files:
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False)
    
    # ========== KULLANICI İŞLEMLERİ ==========
    def get_user(self, user_id):
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        return users.get(str(user_id))
    
    def save_user(self, user_id, username, first_name):
        user_id_str = str(user_id)
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        users[user_id_str] = {
            'username': username,
            'first_name': first_name,
            'user_id': user_id,
            'last_seen': datetime.now(IRAQ_TZ).isoformat(),
            'joined_date': users.get(user_id_str, {}).get('joined_date', datetime.now(IRAQ_TZ).isoformat())
        }
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def get_all_users(self):
        with open(self.users_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # ========== MESAJ İŞLEMLERİ ==========
    def add_message(self, user_id):
        today = datetime.now(IRAQ_TZ).strftime("%Y-%m-%d")
        user_id_str = str(user_id)
        
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        if today not in messages:
            messages[today] = {}
        
        messages[today][user_id_str] = messages[today].get(user_id_str, 0) + 1
        
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        # Saatlik istatistik
        hour_key = datetime.now(IRAQ_TZ).strftime("%Y-%m-%d-%H")
        with open(self.hourly_file, 'r', encoding='utf-8') as f:
            hourly = json.load(f)
        
        if hour_key not in hourly:
            hourly[hour_key] = {}
        
        hourly[hour_key][user_id_str] = hourly[hour_key].get(user_id_str, 0) + 1
        
        with open(self.hourly_file, 'w', encoding='utf-8') as f:
            json.dump(hourly, f, ensure_ascii=False, indent=2)
    
    def get_user_message_count(self, user_id, hours=24):
        user_id_str = str(user_id)
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        since_date = (datetime.now(IRAQ_TZ) - timedelta(hours=hours)).date()
        total = 0
        
        for date_str, daily_msgs in messages.items():
            msg_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if msg_date >= since_date:
                total += daily_msgs.get(user_id_str, 0)
        
        return total
    
    def get_total_message_count(self, user_id):
        user_id_str = str(user_id)
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        total = 0
        for daily_msgs in messages.values():
            total += daily_msgs.get(user_id_str, 0)
        
        return total
    
    def get_all_users_message_counts(self, hours=24):
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        users = self.get_all_users()
        since_date = (datetime.now(IRAQ_TZ) - timedelta(hours=hours)).date()
        
        counts = {}
        for date_str, daily_msgs in messages.items():
            msg_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if msg_date >= since_date:
                for user_id, count in daily_msgs.items():
                    counts[user_id] = counts.get(user_id, 0) + count
        
        result = []
        for user_id, count in counts.items():
            user_data = users.get(user_id, {})
            username = user_data.get('username')
            display = f"@{username}" if username else user_data.get('first_name', '?')
            result.append((display, count, int(user_id)))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result
    
    # ========== ADMİN İŞLEMLERİ ==========
    def save_admins(self, admin_list):
        with open(self.admins_file, 'w', encoding='utf-8') as f:
            json.dump(admin_list, f, ensure_ascii=False, indent=2)
    
    def get_admins(self):
        with open(self.admins_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def is_admin(self, user_id):
        admins = self.get_admins()
        return str(user_id) in admins
    
    # ========== CEZA İŞLEMLERİ ==========
    def update_penalties(self):
        with open(self.penalties_file, 'r', encoding='utf-8') as f:
            penalties = json.load(f)
        
        users = self.get_all_users()
        admins = self.get_admins()
        one_day_ago = datetime.now(IRAQ_TZ) - timedelta(days=1)
        
        for user_id, user_data in users.items():
            if user_id in admins:
                continue
            
            last_seen = datetime.fromisoformat(user_data.get('last_seen', '2000-01-01'))
            if last_seen < one_day_ago:
                if user_id not in penalties:
                    penalties[user_id] = {'count': 0, 'last_message': None}
                penalties[user_id]['count'] = penalties[user_id].get('count', 0) + 1
        
        with open(self.penalties_file, 'w', encoding='utf-8') as f:
            json.dump(penalties, f, ensure_ascii=False, indent=2)
        
        return penalties
    
    def get_users_with_3_penalties(self):
        with open(self.penalties_file, 'r', encoding='utf-8') as f:
            penalties = json.load(f)
        
        users = self.get_all_users()
        admins = self.get_admins()
        result = []
        
        for user_id, data in penalties.items():
            if user_id in admins:
                continue
            if data.get('count', 0) >= 3:
                user_data = users.get(user_id, {})
                username = user_data.get('username')
                display = f"@{username}" if username else user_data.get('first_name', '?')
                result.append((int(user_id), display))
        
        return result
    
    def get_inactive_users_24h(self):
        users = self.get_all_users()
        admins = self.get_admins()
        one_day_ago = datetime.now(IRAQ_TZ) - timedelta(days=1)
        inactive = []
        
        for user_id, user_data in users.items():
            if user_id in admins:
                continue
            last_seen = datetime.fromisoformat(user_data.get('last_seen', '2000-01-01'))
            if last_seen < one_day_ago:
                username = user_data.get('username')
                display = f"@{username}" if username else user_data.get('first_name', '?')
                inactive.append(display)
        
        return inactive
    
    def reset_penalty(self, user_id):
        user_id_str = str(user_id)
        with open(self.penalties_file, 'r', encoding='utf-8') as f:
            penalties = json.load(f)
        
        if user_id_str in penalties:
            penalties[user_id_str]['count'] = 0
            penalties[user_id_str]['last_message'] = datetime.now(IRAQ_TZ).isoformat()
            
            with open(self.penalties_file, 'w', encoding='utf-8') as f:
                json.dump(penalties, f, ensure_ascii=False, indent=2)
    
    # ========== AKTİF SAATLER ==========
    def get_most_active_hours(self, days=7):
        with open(self.hourly_file, 'r', encoding='utf-8') as f:
            hourly = json.load(f)
        
        since = (datetime.now(IRAQ_TZ) - timedelta(days=days)).strftime("%Y-%m-%d")
        
        hour_counts = {}
        for hour_key, users in hourly.items():
            if hour_key >= since:
                hour = hour_key.split('-')[3]
                total = sum(users.values())
                hour_counts[hour] = hour_counts.get(hour, 0) + total
        
        top = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [(f"{h}:00", count) for h, count in top]
