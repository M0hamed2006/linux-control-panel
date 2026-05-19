from datetime import datetime
from enum import Enum

class AlertLevel(Enum):
    """مستويات التنبيهات"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class Alert:
    """فئة التنبيه"""
    def __init__(self, title, message, level, metric_type):
        self.title = title
        self.message = message
        self.level = level
        self.metric_type = metric_type
        self.timestamp = datetime.now().isoformat()
        self.read = False
    
    def to_dict(self):
        return {
            'title': self.title,
            'message': self.message,
            'level': self.level.value,
            'metric_type': self.metric_type,
            'timestamp': self.timestamp,
            'read': self.read
        }

class AlertMonitor:
    """خدمة مراقبة التنبيهات"""
    
    def __init__(self):
        self.alerts = []
        self.max_alerts = 100
        self.thresholds = {
            'cpu_warning': 70,
            'cpu_critical': 90,
            'memory_warning': 75,
            'memory_critical': 90,
            'disk_warning': 80,
            'disk_critical': 95,
            'temperature_warning': 80,
            'temperature_critical': 95
        }
    
    def check_cpu(self, cpu_percent):
        """فحص استخدام CPU"""
        alerts = []
        
        if cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append(Alert(
                '🔴 CPU Critical',
                f'استخدام المعالج وصل إلى {cpu_percent:.1f}%',
                AlertLevel.CRITICAL,
                'cpu'
            ))
        elif cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append(Alert(
                '🟡 CPU Warning',
                f'استخدام المعالج {cpu_percent:.1f}%',
                AlertLevel.WARNING,
                'cpu'
            ))
        
        return alerts
    
    def check_memory(self, memory_percent):
        """فحص استخدام الذاكرة"""
        alerts = []
        
        if memory_percent >= self.thresholds['memory_critical']:
            alerts.append(Alert(
                '🔴 Memory Critical',
                f'استخدام الذاكرة وصل إلى {memory_percent:.1f}%',
                AlertLevel.CRITICAL,
                'memory'
            ))
        elif memory_percent >= self.thresholds['memory_warning']:
            alerts.append(Alert(
                '🟡 Memory Warning',
                f'استخدام الذاكرة {memory_percent:.1f}%',
                AlertLevel.WARNING,
                'memory'
            ))
        
        return alerts
    
    def check_disk(self, disk_percent):
        """فحص استخدام القرص"""
        alerts = []
        
        if disk_percent >= self.thresholds['disk_critical']:
            alerts.append(Alert(
                '🔴 Disk Critical',
                f'استخدام القرص وصل إلى {disk_percent:.1f}%',
                AlertLevel.CRITICAL,
                'disk'
            ))
        elif disk_percent >= self.thresholds['disk_warning']:
            alerts.append(Alert(
                '🟡 Disk Warning',
                f'استخدام القرص {disk_percent:.1f}%',
                AlertLevel.WARNING,
                'disk'
            ))
        
        return alerts
    
    def add_alert(self, alert):
        """إضافة تنبيه"""
        self.alerts.insert(0, alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop()
    
    def add_alerts(self, alerts):
        """إضافة عدة تنبيهات"""
        for alert in alerts:
            self.add_alert(alert)
    
    def get_alerts(self, limit=50, level=None):
        """الحصول على التنبيهات"""
        alerts = self.alerts
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return [a.to_dict() for a in alerts[:limit]]
    
    def get_unread_count(self):
        """عدد التنبيهات غير المقروءة"""
        return len([a for a in self.alerts if not a.read])
    
    def mark_as_read(self, index):
        """تحديد التنبيه كمقروء"""
        if 0 <= index < len(self.alerts):
            self.alerts[index].read = True
    
    def clear_alerts(self):
        """حذف كل التنبيهات"""
        self.alerts = []
    
    def check_all(self, cpu, memory, disk):
        """فحص كل الموارد"""
        alerts = []
        alerts.extend(self.check_cpu(cpu))
        alerts.extend(self.check_memory(memory))
        alerts.extend(self.check_disk(disk))
        
        for alert in alerts:
            self.add_alert(alert)
        
        return alerts
    
    def set_threshold(self, metric, level, value):
        """تعديل حد التنبيه"""
        key = f'{metric}_{level}'
        if key in self.thresholds:
            self.thresholds[key] = value
            return True
        return False
    
    def get_thresholds(self):
        """الحصول على حدود التنبيهات"""
        return self.thresholds
