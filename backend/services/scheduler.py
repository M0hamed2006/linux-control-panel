import schedule
import time
import threading
from datetime import datetime
from services.database import Database

class Scheduler:
    """جدول المهام"""
    
    def __init__(self):
        self.db = Database()
        self.jobs = []
        self.running = False
    
    def add_job(self, job_name, func, interval, interval_type='seconds'):
        """إضافة مهمة"""
        if interval_type == 'seconds':
            schedule.every(interval).seconds.do(func)
        elif interval_type == 'minutes':
            schedule.every(interval).minutes.do(func)
        elif interval_type == 'hours':
            schedule.every(interval).hours.do(func)
        elif interval_type == 'days':
            schedule.every(interval).days.do(func)
        
        self.jobs.append({'name': job_name, 'interval': interval, 'type': interval_type})
        print(f"✅ Job added: {job_name}")
    
    def cleanup_old_data(self):
        """تنظيف البيانات القديمة"""
        print(f"🧹 Cleaning old data... {datetime.now()}")
        self.db.cleanup_old_stats(days=30)
    
    def backup_database(self):
        """نسخ احتياطي"""
        print(f"💾 Backing up database... {datetime.now()}")
        # يمكن إضافة كود النسخ الاحتياطي هنا
    
    def start(self):
        """بدء الجدول"""
        self.running = True
        
        # إضافة المهام
        self.add_job('cleanup', self.cleanup_old_data, 1, 'days')
        self.add_job('backup', self.backup_database, 6, 'hours')
        
        print("⏰ Scheduler started")
        
        # تشغيل في thread منفصل
        thread = threading.Thread(target=self._run_scheduler)
        thread.daemon = True
        thread.start()
    
    def _run_scheduler(self):
        """تشغيل الجدول"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """إيقاف الجدول"""
        self.running = False
        print("⏱️ Scheduler stopped")
    
    def get_jobs(self):
        """الحصول على المهام"""
        return self.jobs
