import psutil
from datetime import datetime

class SystemMonitor:
    @staticmethod
    def get_cpu_info():
        return {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'frequency': psutil.cpu_freq().current
        }
    
    @staticmethod
    def get_memory_info():
        memory = psutil.virtual_memory()
        return {
            'total': memory.total / (1024**3),
            'used': memory.used / (1024**3),
            'available': memory.available / (1024**3),
            'percent': memory.percent
        }
    
    @staticmethod
    def get_disk_info():
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total / (1024**3),
            'used': disk.used / (1024**3),
            'free': disk.free / (1024**3),
            'percent': disk.percent
        }
    
    @staticmethod
    def get_network_info():
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
    
    @staticmethod
    def get_process_count():
        return len(psutil.pids())
    
    @staticmethod
    def get_uptime():
        from datetime import datetime, timedelta
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        return str(uptime).split('.')[0]
