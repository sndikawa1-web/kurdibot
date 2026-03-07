# database.py
import sqlite3
import datetime
from config import DB_NAME, XP_PER_MESSAGE

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        print("✅ Veritabanı bağlantısı kuruldu")
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                messages_count INTEGER DEFAULT 0,
                last_message_date TEXT,
                joined_date TEXT
            )
        ''')
        self.conn.commit()
        print("✅ Tablolar oluşturuldu")
    
    def add_user(self, user_id, username, first_name, last_name):
        try:
            now = datetime.datetime.now().isoformat()
            self.cursor.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name, joined_date) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, now))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ add_user hatası: {e}")
            return False
    
    def update_user_activity(self, user_id):
        try:
            now = datetime.datetime.now().isoformat()
            
            self.cursor.execute('SELECT xp, level, messages_count FROM users WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            
            if result:
                xp, level, messages_count = result
                new_xp = xp + XP_PER_MESSAGE
                new_messages_count = messages_count + 1
                new_level = (new_xp // 100) + 1
                if new_level > 70:
                    new_level = 70
                
                self.cursor.execute('''
                    UPDATE users 
                    SET xp = ?, level = ?, messages_count = ?, last_message_date = ?
                    WHERE user_id = ?
                ''', (new_xp, new_level, new_messages_count, now, user_id))
                
                self.conn.commit()
                
                if new_level > level:
                    return True, new_level
            return False, None
        except Exception as e:
            print(f"❌ update_user_activity hatası: {e}")
            return False, None
    
    def get_user_stats(self, user_id):
        try:
            self.cursor.execute('''
                SELECT username, first_name, xp, level, messages_count, last_message_date 
                FROM users WHERE user_id = ?
            ''', (user_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"❌ get_user_stats hatası: {e}")
            return None
    
    def get_top_users(self, limit=10):
        try:
            self.cursor.execute('''
                SELECT user_id, username, first_name, xp, level, messages_count 
                FROM users 
                ORDER BY level DESC, xp DESC 
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ get_top_users hatası: {e}")
            return []
    
    def get_inactive_users_24h(self):
        try:
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
            
            self.cursor.execute('SELECT user_id, username, first_name FROM users')
            all_users = self.cursor.fetchall()
            
            self.cursor.execute('SELECT DISTINCT user_id FROM users WHERE last_message_date > ?', (yesterday,))
            active_users = set([row[0] for row in self.cursor.fetchall()])
            
            return [user for user in all_users if user[0] not in active_users]
        except Exception as e:
            print(f"❌ get_inactive_users_24h hatası: {e}")
            return []
    
    def close(self):
        self.conn.close()
