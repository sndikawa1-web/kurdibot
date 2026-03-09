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
            
            # İsim güncelleme (her zaman yap)
            self.cursor.execute('''
                UPDATE users 
                SET username = ?, first_name = ?, last_name = ?
                WHERE user_id = ?
            ''', (username, first_name, last_name, user_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ add_user hatası: {e}")
            return False
    
    def calculate_level_from_xp(self, xp):
        """ULTRA ZOR level sistemi - XP'den level hesapla"""
        
        # Level 1-10 (100 XP each)
        if xp < 1000:
            return (xp // 100) + 1
        
        # Level 11-15 (200 XP each)
        elif xp < 2000:  # 1100-1900
            return 11 + ((xp - 1000) // 200)
        
        # Level 16-20 (300 XP each)
        elif xp < 3500:  # 2200-3400
            return 16 + ((xp - 2000) // 300)
        
        # Level 21-25 (400 XP each)
        elif xp < 5500:  # 3800-5400
            return 21 + ((xp - 3500) // 400)
        
        # Level 26-30 (500 XP each)
        elif xp < 8000:  # 5900-7900
            return 26 + ((xp - 5500) // 500)
        
        # Level 31-35 (800 XP each) - AŞIRI ZOR
        elif xp < 12000:  # 8700-11900
            return 31 + ((xp - 8000) // 800)
        
        # Level 36-40 (1200 XP each) - ÇOK AŞIRI ZOR
        elif xp < 18000:  # 13100-17900
            return 36 + ((xp - 12000) // 1200)
        
        # Level 41-45 (1800 XP each) - İMKANSIZ
        elif xp < 27000:  # 19700-26900
            return 41 + ((xp - 18000) // 1800)
        
        # Level 46-50 (2500 XP each) - DELİLİK
        elif xp < 39500:  # 29400-39400
            return 46 + ((xp - 27000) // 2500)
        
        # Level 51-55 (3500 XP each) - ÇILGINLIK
        elif xp < 57000:  # 42900-56900
            return 51 + ((xp - 39500) // 3500)
        
        # Level 56-60 (5000 XP each) - EFSANEVİ
        elif xp < 82000:  # 61900-81900
            return 56 + ((xp - 57000) // 5000)
        
        # Level 61-65 (7000 XP each) - MİTOLOJİK
        elif xp < 117000:  # 88900-116900
            return 61 + ((xp - 82000) // 7000)
        
        # Level 66-70 (10000 XP each) - TANRISAL
        else:
            level = 66 + ((xp - 117000) // 10000)
            return min(level, 70)
    
    def update_user_activity(self, user_id):
        try:
            now = datetime.datetime.now().isoformat()
            
            self.cursor.execute('SELECT xp, level, messages_count FROM users WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            
            if result:
                xp, level, messages_count = result
                new_xp = xp + XP_PER_MESSAGE
                new_messages_count = messages_count + 1
                new_level = self.calculate_level_from_xp(new_xp)
                
                self.cursor.execute('''
                    UPDATE users 
                    SET xp = ?, level = ?, messages_count = ?, last_message_date = ?
                    WHERE user_id = ?
                ''', (new_xp, new_level, new_messages_count, now, user_id))
                
                self.conn.commit()
                
                if new_level > level:
                    print(f"🎯 Level atlama: {level} -> {new_level}")
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
    
    def get_inactive_users_3days(self):
        try:
            three_days_ago = (datetime.datetime.now() - datetime.timedelta(days=3)).isoformat()
            
            self.cursor.execute('''
                SELECT user_id, username, first_name, last_message_date 
                FROM users 
                WHERE last_message_date < ? OR last_message_date IS NULL
            ''', (three_days_ago,))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ get_inactive_users_3days hatası: {e}")
            return []
    
    def close(self):
        self.conn.close()
