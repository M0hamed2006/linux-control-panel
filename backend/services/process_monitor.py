import psutil
from datetime import datetime

class ProcessMonitor:
    """خدمة مراقبة العمليات"""
    
    @staticmethod
    def get_top_processes(n=10, sort_by='cpu'):
        """الحصول على أعلى N عمليات"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'] or 0,
                        'memory_percent': proc.info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # ترتيب حسب النوع
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            else:
                processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            return processes[:n]
        except Exception as e:
            print(f"Process Monitor Error: {e}")
            return []
    
    @staticmethod
    def get_process_details(pid):
        """الحصول على تفاصيل عملية معينة"""
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'memory_mb': proc.memory_info().rss / (1024 ** 2),
                'create_time': datetime.fromtimestamp(proc.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
                'exe': proc.exe() if hasattr(proc, 'exe') else 'N/A',
                'cmdline': ' '.join(proc.cmdline()) if proc.cmdline() else 'N/A'
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def kill_process(pid):
        """إيقاف عملية"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return {'success': True, 'message': f'Process {pid} terminated'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_all_processes():
        """الحصول على كل العمليات"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'status': proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return processes
        except Exception as e:
            return []
