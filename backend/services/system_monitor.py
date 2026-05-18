import psutil
from datetime import datetime, timedelta

class SystemMonitor:
    """خدمة مراقبة النظام - محسّنة للـ Realtime"""
    
    @staticmethod
    def get_cpu_info():
        """الحصول على معلومات المعالج"""
        try:
            return {
                'percent': psutil.cpu_percent(interval=0.1),
                'count': psutil.cpu_count(),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'per_core': psutil.cpu_percent(interval=0.1, percpu=True)
            }
        except Exception as e:
            print(f"CPU Error: {e}")
            return {'percent': 0, 'count': 0, 'frequency': 0, 'per_core': []}
    
    @staticmethod
    def get_memory_info():
        """الحصول على معلومات الذاكرة"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                'total': round(memory.total / (1024**3), 2),
                'used': round(memory.used / (1024**3), 2),
                'available': round(memory.available / (1024**3), 2),
                'percent': memory.percent,
                'swap_total': round(swap.total / (1024**3), 2),
                'swap_used': round(swap.used / (1024**3), 2),
                'swap_percent': swap.percent
            }
        except Exception as e:
            print(f"Memory Error: {e}")
            return {'total': 0, 'used': 0, 'available': 0, 'percent': 0}
    
    @staticmethod
    def get_disk_info():
        """الحصول على معلومات القرص"""
        try:
            disk = psutil.disk_usage('/')
            return {
                'total': round(disk.total / (1024**3), 2),
                'used': round(disk.used / (1024**3), 2),
                'free': round(disk.free / (1024**3), 2),
                'percent': disk.percent
            }
        except Exception as e:
            print(f"Disk Error: {e}")
            return {'total': 0, 'used': 0, 'free': 0, 'percent': 0}
    
    @staticmethod
    def get_network_info():
        """الحصول على معلومات الشبكة"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'dropped_in': net_io.dropin,
                'dropped_out': net_io.dropout
            }
        except Exception as e:
            print(f"Network Error: {e}")
            return {'bytes_sent': 0, 'bytes_recv': 0}
    
    @staticmethod
    def get_process_count():
        """عدد العمليات"""
        try:
            return len(psutil.pids())
        except Exception as e:
            print(f"Process Error: {e}")
            return 0
    
    @staticmethod
    def get_uptime():
        """وقت تشغيل النظام"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            return {
                'total_seconds': int(uptime.total_seconds()),
                'formatted': str(uptime).split('.')[0],
                'boot_time': boot_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"Uptime Error: {e}")
            return {'total_seconds': 0, 'formatted': '00:00:00'}
    
    @staticmethod
    def get_all_system_info():
        """الحصول على كل معلومات النظام دفعة واحدة"""
        return {
            'cpu': SystemMonitor.get_cpu_info(),
            'memory': SystemMonitor.get_memory_info(),
            'disk': SystemMonitor.get_disk_info(),
            'network': SystemMonitor.get_network_info(),
            'process_count': SystemMonitor.get_process_count(),
            'uptime': SystemMonitor.get_uptime(),
            'timestamp': datetime.now().isoformat()
        }
