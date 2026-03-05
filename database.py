# ==================== VERİTABANI (TEK DOSYA) ====================
import json
import os
from datetime import datetime, timedelta
from messages import IRAQ_TZ

class Database:
    def __init__(self):
        self.users_file = 'users.json'
        self.messages_file = 'messages.json'
        self.penalties_file = 'penalties.json'
        self.admins_file = 'admins.json'
        self.achievements_file = 'achievements.json'
        self.levels_file = 'levels.json'
        self.records_file = 'records.json'
        self.hourly_file = 'hourly_stats.json'
        self.load_data()
    
    def load_data(self):
        files = [self.users_file, self.messages_file, self.penalties_file, 
                 self.admins_file, self.achievements_file, self.levels_file,
                 self.records_file, self.hourly_file]
        for file in files:
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False)
    
    # Kullanıcı işlemleri
    def save_admins(self, admin_list):
        with open(self.admins_file, 'w', encoding='utf-8') as f:
            json.dump(admin_list, f, ensure_ascii=False, indent=2)
    
    def get_admins(self):
        with open(self.admins_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def is_admin(self, user_id):
        admins = self.get_admins()
        return str(user_id) in admins
    
    def add_message(self, user_id, username, first_name):
        today = datetime.now(IRAQ_TZ).strftime("%Y-%m-%d")
        user_id_str = str(user_id)
        
        # Kullanıcıyı kaydet
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        users[user_id_str] = {
            'username': username,
            'first_name': first_name,
            'user_id': user_id,
            'last_seen': datetime.now(IRAQ_TZ).isoformat()
        }
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        # Mesaj sayısını güncelle
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        if today not in messages:
            messages[today] = {}
        
        if user_id_str not in messages[today]:
            messages[today][user_id_str] = 0
        
        messages[today][user_id_str] += 1
        
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        # Eksiyi sıfırla
        if not self.is_admin(user_id):
            with open(self.penalties_file, 'r', encoding='utf-8') as f:
                penalties = json.load(f)
            
            penalties[user_id_str] = {
                'count': 0,
                'last_message': datetime.now(IRAQ_TZ).isoformat()
            }
            
            with open(self.penalties_file, 'w', encoding='utf-8') as f:
                json.dump(penalties, f, ensure_ascii=False, indent=2)
    
    def get_all_users_message_counts_24h(self):
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        since_date = (datetime.now(IRAQ_TZ) - timedelta(hours=24)).date()
        
        user_counts = {}
        for date_str, daily_msgs in messages.items():
            msg_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if msg_date >= since_date:
                for user_id, count in daily_msgs.items():
                    if count > 0:
                        user_counts[user_id] = user_counts.get(user_id, 0) + count
        
        result = []
        for user_id, count in user_counts.items():
            user_data = users.get(user_id, {})
            username = user_data.get('username')
            if username:
                display_name = f"@{username}"
            else:
                display_name = user_data.get('first_name', 'Bilinmiyor')
            result.append((display_name, count, user_id))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result
    
    def get_inactive_users_24h(self):
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        admins = self.get_admins()
        one_day_ago = datetime.now(IRAQ_TZ) - timedelta(days=1)
        inactive = []
        
        for user_id, user_data in users.items():
            if user_id in admins:
                continue
            last_seen = datetime.fromisoformat(user_data.get('last_seen', '2000-01-01'))
            if last_seen < one_day_ago:
                username = user_data.get('username')
                if username:
                    inactive.append(f"@{username}")
                else:
                    inactive.append(user_data.get('first_name', 'Bilinmiyor'))
        
        return inactive
    
    def get_users_with_3_penalties(self):
        with open(self.penalties_file, 'r', encoding='utf-8') as f:
            penalties = json.load(f)
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        admins = self.get_admins()
        result = []
        
        for user_id, penalty_data in penalties.items():
            if user_id in admins:
                continue
            if penalty_data.get('count', 0) >= 3:
                user_data = users.get(user_id, {})
                username = user_data.get('username')
                user_id_int = user_data.get('user_id')
                if username:
                    result.append((user_id_int, f"@{username}"))
                else:
                    result.append((user_id_int, user_data.get('first_name', 'Bilinmiyor')))
        
        return result
    
    # Gelişmiş özellikler
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
        
        top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [(f"{h}:00", count) for h, count in top_hours]
