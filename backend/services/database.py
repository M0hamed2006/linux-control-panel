import sqlite3
import json
from datetime import datetime
import os

class Database:
    """خدمة قاعدة البيانات"""
    
    def __init__(self, db_path='data/system_monitor.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """إنشاء قاعدة البيانات والجداول"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول البيانات التاريخية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                network_sent INTEGER,
                network_recv INTEGER,
                process_count INTEGER
            )
        ''')
        
        # جدول التنبيهات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                message TEXT,
                level TEXT,
                metric_type TEXT,
                read BOOLEAN DEFAULT 0
            )
        ''')
        
        # جدول السجلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                log_type TEXT,
                log_message TEXT,
                severity TEXT
            )
        ''')
        
        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_system_stats(self, cpu, memory, disk, network_sent, network_recv, process_count):
        """إدراج إحصائيات النظام"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_stats 
                (cpu_percent, memory_percent, disk_percent, network_sent, network_recv, process_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cpu, memory, disk, network_sent, network_recv, process_count))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False
    
    def insert_alert(self, title, message, level, metric_type):
        """إدراج تنبيه"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (title, message, level, metric_type)
                VALUES (?, ?, ?, ?)
            ''', (title, message, level, metric_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False
    
    def get_system_stats(self, hours=24):
        """الحصول على إحصائيات النظام"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT * FROM system_stats 
                WHERE timestamp >= datetime('now', '-{hours} hours')
                ORDER BY timestamp DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            print(f"Database Error: {e}")
            return []
    
    def get_alerts(self, limit=100):
        """الحصول على التنبيهات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            print(f"Database Error: {e}")
            return []
    
    def mark_alert_as_read(self, alert_id):
        """تحديد التنبيه كمقروء"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE alerts SET read = 1 WHERE id = ?', (alert_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False
    
    def get_unread_alerts_count(self):
        """عدد التنبيهات غير المقروءة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE read = 0')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
        except Exception as e:
            print(f"Database Error: {e}")
            return 0
    
    def insert_log(self, log_type, message, severity='info'):
        """إدراج سجل"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_logs (log_type, log_message, severity)
                VALUES (?, ?, ?)
            ''', (log_type, message, severity))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False
    
    def get_logs(self, log_type=None, limit=100):
        """الحصول على السجلات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if log_type:
                cursor.execute('''
                    SELECT * FROM system_logs 
                    WHERE log_type = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (log_type, limit))
            else:
                cursor.execute('''
                    SELECT * FROM system_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            print(f"Database Error: {e}")
            return []
    
    def set_setting(self, key, value):
        """حفظ إعداد"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """الحصول على إعداد"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else default
        except Exception as e:
            print(f"Database Error: {e}")
            return default
    
    def cleanup_old_stats(self, days=30):
        """حذف الإحصائيات القديمة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                DELETE FROM system_stats 
                WHERE timestamp < datetime('now', '-{days} days')
            ''')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False
