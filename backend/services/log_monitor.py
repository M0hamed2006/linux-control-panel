import os
import subprocess
from datetime import datetime, timedelta

class LogMonitor:
    """خدمة مراقبة الـ Logs"""
    
    # مسارات الـ Logs الأساسية
    LOG_PATHS = {
        'system': '/var/log/syslog',
        'auth': '/var/log/auth.log',
        'kernel': '/var/log/kern.log',
        'messages': '/var/log/messages',
        'boot': '/var/log/boot.log'
    }
    
    @staticmethod
    def get_log_file(log_type, lines=50):
        """قراءة ملف log معين"""
        try:
            log_path = LogMonitor.LOG_PATHS.get(log_type)
            
            if not log_path or not os.path.exists(log_path):
                return {'error': f'Log file not found: {log_type}'}
            
            result = subprocess.run(
                ['tail', '-n', str(lines), log_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            log_lines = result.stdout.strip().split('\n')
            return {
                'type': log_type,
                'lines': log_lines,
                'count': len(log_lines)
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_recent_errors(lines=20):
        """الحصول على آخر الأخطاء"""
        try:
            result = subprocess.run(
                ['grep', '-i', 'error', '/var/log/syslog'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            errors = result.stdout.strip().split('\n')[-lines:]
            return {
                'errors': [e for e in errors if e],
                'count': len([e for e in errors if e])
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_recent_warnings(lines=20):
        """الحصول على آخر التحذيرات"""
        try:
            result = subprocess.run(
                ['grep', '-i', 'warning', '/var/log/syslog'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            warnings = result.stdout.strip().split('\n')[-lines:]
            return {
                'warnings': [w for w in warnings if w],
                'count': len([w for w in warnings if w])
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def search_logs(keyword, log_type='system', lines=50):
        """البحث عن كلمة مفتاحية في الـ logs"""
        try:
            log_path = LogMonitor.LOG_PATHS.get(log_type)
            
            if not log_path or not os.path.exists(log_path):
                return {'error': f'Log file not found: {log_type}'}
            
            result = subprocess.run(
                ['grep', '-i', keyword, log_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            results = result.stdout.strip().split('\n')[-lines:]
            return {
                'keyword': keyword,
                'results': [r for r in results if r],
                'count': len([r for r in results if r])
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_failed_login_attempts():
        """الحصول على محاولات تسجيل دخول فاشلة"""
        try:
            result = subprocess.run(
                ['grep', 'Failed password', '/var/log/auth.log'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            attempts = result.stdout.strip().split('\n')
            return {
                'failed_attempts': [a for a in attempts if a],
                'count': len([a for a in attempts if a])
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_sudo_commands(lines=20):
        """الحصول على آخر أوامر sudo"""
        try:
            result = subprocess.run(
                ['grep', 'sudo', '/var/log/auth.log'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            commands = result.stdout.strip().split('\n')[-lines:]
            return {
                'sudo_commands': [c for c in commands if c],
                'count': len([c for c in commands if c])
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_disk_space_logs():
        """الحصول على تحذيرات مساحة القرص"""
        try:
            result = subprocess.run(
                ['grep', '-i', 'disk', '/var/log/syslog'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            logs = result.stdout.strip().split('\n')[-20:]
            return {
                'disk_logs': [l for l in logs if l],
                'count': len([l for l in logs if l])
            }
        except Exception as e:
            return {'error': str(e)}
