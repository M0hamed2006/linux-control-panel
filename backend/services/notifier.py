import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class Notifier:
    """نظام الإشعارات"""
    
    def __init__(self):
        self.notifications = []
        self.max_notifications = 1000
    
    def add_notification(self, title, message, level='info'):
        """إضافة إشعار"""
        notification = {
            'id': len(self.notifications),
            'title': title,
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        self.notifications.insert(0, notification)
        
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop()
        
        return notification
    
    def send_desktop_notification(self, title, message):
        """إشعار سطح المكتب"""
        try:
            subprocess.run(
                ['notify-send', '-u', 'critical', title, message],
                timeout=5
            )
            return True
        except Exception as e:
            print(f"Desktop Notification Error: {e}")
            return False
    
    def send_email(self, to_email, subject, body, smtp_server='localhost', smtp_port=25):
        """إرسال بريد"""
        try:
            msg = MIMEMultipart()
            msg['From'] = 'linux-control-panel@localhost'
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email Error: {e}")
            return False
    
    def get_notifications(self, limit=50):
        """الحصول على الإشعارات"""
        return self.notifications[:limit]
    
    def mark_as_read(self, notification_id):
        """تحديد كمقروء"""
        for notif in self.notifications:
            if notif['id'] == notification_id:
                notif['read'] = True
                return True
        return False
    
    def get_unread_count(self):
        """عدد الإشعارات غير المقروءة"""
        return len([n for n in self.notifications if not n['read']])
