# database.py
import sqlite3
import datetime
from config import DB_NAME, XP_PER_MESSAGE

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
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
                joined_date TEXT,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                added_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name, last_name):
        now = datetime.datetime.now().isoformat()
        self.cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, joined_date) 
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, now))
        self.conn.commit()
    
    def update_user_activity(self, user_id):
        now = datetime.datetime.now().isoformat()
        
        self.cursor.execute('SELECT xp, level, messages_count FROM users WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        
        if result:
            xp, level, messages_count = result
            new_xp = xp + XP_PER_MESSAGE
            new_messages_count = messages_count + 1
            new_level = self.calculate_level(new_xp)
            
            self.cursor.execute('''
                INSERT INTO messages (user_id, message_date) VALUES (?, ?)
            ''', (user_id, now))
            
            self.cursor.execute('''
                UPDATE users 
                SET xp = ?, level = ?, messages_count = ?, last_message_date = ?
                WHERE user_id = ?
            ''', (new_xp, new_level, new_messages_count, now, user_id))
            
            self.conn.commit()
            
            if new_level > level:
                return True, new_level, self.get_level_title(new_level)
        
        return False, None, None
    
    def calculate_level(self, xp):
        level = (xp // 100) + 1
        return min(level, 70)
    
    def get_level_title(self, level):
        if level <= 10:
            return "Diamond 💎"
        elif level <= 19:
            return "Pro ⚡"
        elif level <= 29:
            return "Pro Leader 👑⚡"
        elif level <= 39:
            return "King 👑"
        elif level <= 49:
            return "Dragon 🐉"
        elif level <= 59:
            return "Myth 🔱✨"
        else:
            return "King Dragon 👑🐉"
    
    def get_user_stats(self, user_id):
        self.cursor.execute('''
            SELECT username, first_name, xp, level, messages_count, last_message_date 
            FROM users WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchone()
    
    def get_top_users(self, limit=10):
        self.cursor.execute('''
            SELECT user_id, username, first_name, xp, level, messages_count 
            FROM users 
            ORDER BY level DESC, xp DESC 
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def get_inactive_users_24h(self):
        now = datetime.datetime.now()
        yesterday = (now - datetime.timedelta(days=1)).isoformat()
        
        self.cursor.execute('''
            SELECT DISTINCT user_id FROM messages 
            WHERE message_date > ?
        ''', (yesterday,))
        
        active_users = set([row[0] for row in self.cursor.fetchall()])
        
        self.cursor.execute('SELECT user_id, username, first_name FROM users')
        all_users = self.cursor.fetchall()
        
        inactive = [user for user in all_users if user[0] not in active_users]
        return inactive
    
    def get_inactive_users_3days(self):
        now = datetime.datetime.now()
        three_days_ago = (now - datetime.timedelta(days=3)).isoformat()
        
        self.cursor.execute('''
            SELECT user_id, username, first_name, last_message_date 
            FROM users 
            WHERE last_message_date < ? OR last_message_date IS NULL
        ''', (three_days_ago,))
        
        return self.cursor.fetchall()
    
    def update_admin_status(self, user_id, is_admin):
        self.cursor.execute('''
            UPDATE users SET is_admin = ? WHERE user_id = ?
        ''', (1 if is_admin else 0, user_id))
        
        if is_admin:
            now = datetime.datetime.now().isoformat()
            self.cursor.execute('''
                INSERT OR IGNORE INTO admins_log (user_id, added_date) VALUES (?, ?)
            ''', (user_id, now))
        
        self.conn.commit()
    
    def get_all_users(self):
        self.cursor.execute('SELECT user_id, username, first_name FROM users')
        return self.cursor.fetchall()
    
    def get_weekly_stats(self):
        now = datetime.datetime.now()
        week_ago = (now - datetime.timedelta(days=7)).isoformat()
        
        self.cursor.execute('''
            SELECT user_id, COUNT(*) as msg_count 
            FROM messages 
            WHERE message_date > ? 
            GROUP BY user_id 
            ORDER BY msg_count DESC 
            LIMIT 10
        ''', (week_ago,))
        
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()
