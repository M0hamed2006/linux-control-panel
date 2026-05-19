import psutil
from datetime import datetime, timedelta
from collections import deque
import statistics

class PerformanceAnalyzer:
    """تحليل أداء النظام"""
    
    def __init__(self, max_history=3600):
        self.max_history = max_history
        self.cpu_history = deque(maxlen=max_history)
        self.memory_history = deque(maxlen=max_history)
        self.disk_history = deque(maxlen=max_history)
        self.timestamps = deque(maxlen=max_history)
    
    def record_metrics(self, cpu, memory, disk):
        """تسجيل المقاييس"""
        self.cpu_history.append(cpu)
        self.memory_history.append(memory)
        self.disk_history.append(disk)
        self.timestamps.append(datetime.now().isoformat())
    
    def get_average_cpu(self, minutes=60):
        """متوسط CPU"""
        if not self.cpu_history:
            return 0
        return statistics.mean(list(self.cpu_history)[-minutes:]) if minutes < len(self.cpu_history) else statistics.mean(self.cpu_history)
    
    def get_average_memory(self, minutes=60):
        """متوسط Memory"""
        if not self.memory_history:
            return 0
        return statistics.mean(list(self.memory_history)[-minutes:]) if minutes < len(self.memory_history) else statistics.mean(self.memory_history)
    
    def get_peak_cpu(self, minutes=60):
        """ذروة CPU"""
        if not self.cpu_history:
            return 0
        data = list(self.cpu_history)[-minutes:] if minutes < len(self.cpu_history) else self.cpu_history
        return max(data) if data else 0
    
    def get_peak_memory(self, minutes=60):
        """ذروة Memory"""
        if not self.memory_history:
            return 0
        data = list(self.memory_history)[-minutes:] if minutes < len(self.memory_history) else self.memory_history
        return max(data) if data else 0
    
    def detect_anomalies(self, threshold=3):
        """كشف الشذوذ"""
        anomalies = []
        
        # تحليل CPU
        if len(self.cpu_history) > 10:
            cpu_mean = statistics.mean(self.cpu_history)
            cpu_std = statistics.stdev(self.cpu_history)
            current_cpu = self.cpu_history[-1]
            
            if current_cpu > cpu_mean + (threshold * cpu_std):
                anomalies.append({
                    'type': 'CPU',
                    'value': current_cpu,
                    'mean': cpu_mean,
                    'severity': 'high' if current_cpu > cpu_mean + (threshold * 2 * cpu_std) else 'medium'
                })
        
        # تحليل Memory
        if len(self.memory_history) > 10:
            mem_mean = statistics.mean(self.memory_history)
            mem_std = statistics.stdev(self.memory_history)
            current_mem = self.memory_history[-1]
            
            if current_mem > mem_mean + (threshold * mem_std):
                anomalies.append({
                    'type': 'Memory',
                    'value': current_mem,
                    'mean': mem_mean,
                    'severity': 'high' if current_mem > mem_mean + (threshold * 2 * mem_std) else 'medium'
                })
        
        return anomalies
    
    def get_trend(self, metric='cpu', minutes=60):
        """اتجاه المقياس"""
        if metric == 'cpu':
            data = list(self.cpu_history)[-minutes:]
        elif metric == 'memory':
            data = list(self.memory_history)[-minutes:]
        else:
            data = list(self.disk_history)[-minutes:]
        
        if len(data) < 2:
            return 'stable'
        
        first_half = statistics.mean(data[:len(data)//2])
        second_half = statistics.mean(data[len(data)//2:])
        
        if second_half > first_half * 1.1:
            return 'increasing'
        elif second_half < first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_report(self):
        """تقرير شامل"""
        return {
            'cpu': {
                'current': self.cpu_history[-1] if self.cpu_history else 0,
                'average': self.get_average_cpu(),
                'peak': self.get_peak_cpu(),
                'trend': self.get_trend('cpu')
            },
            'memory': {
                'current': self.memory_history[-1] if self.memory_history else 0,
                'average': self.get_average_memory(),
                'peak': self.get_peak_memory(),
                'trend': self.get_trend('memory')
            },
            'disk': {
                'current': self.disk_history[-1] if self.disk_history else 0,
                'average': statistics.mean(self.disk_history) if self.disk_history else 0,
                'peak': max(self.disk_history) if self.disk_history else 0,
            },
            'anomalies': self.detect_anomalies()
        }
