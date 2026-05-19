import subprocess
import re
from datetime import datetime, timedelta
from collections import defaultdict

class SecurityMonitor:
    """خدمة المراقبة الأمنية"""
    
    def __init__(self):
        self.failed_logins = defaultdict(list)
        self.open_ports_history = {}
        self.suspicious_processes = {
            'xmrig', 'minerd', 'crypto', 'miner', 'backdoor', 'shell', 'nc', 'bash'
        }
    
    def get_failed_login_attempts(self, hours=24):
        """محاولات الدخول الفاشلة"""
        try:
            result = subprocess.run(
                ['grep', 'Failed password', '/var/log/auth.log'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            attempts = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    match = re.search(r'(\w+ \d+ \d+:\d+:\d+).*?(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        attempts.append({
                            'timestamp': match.group(1),
                            'ip': match.group(2),
                            'log': line
                        })
            
            return sorted(attempts, key=lambda x: x['timestamp'], reverse=True)[:100]
        except:
            return []
    
    def detect_brute_force(self, threshold=10, minutes=2):
        """كشف محاولات brute force"""
        try:
            attempts = self.get_failed_login_attempts()
            now = datetime.now()
            
            ip_attempts = defaultdict(list)
            for attempt in attempts:
                ip = attempt['ip']
                ip_attempts[ip].append(attempt)
            
            suspicious = []
            for ip, ip_list in ip_attempts.items():
                if len(ip_list) >= threshold:
                    suspicious.append({
                        'ip': ip,
                        'attempts': len(ip_list),
                        'alert': f'🚨 محاولات اختراق من {ip}'
                    })
            
            return suspicious
        except:
            return []
    
    def get_open_ports(self):
        """المنافذ المفتوحة"""
        try:
            result = subprocess.run(
                ['netstat', '-tuln'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            ports = []
            for line in result.stdout.split('\n'):
                if 'LISTEN' in line:
                    match = re.search(r'tcp\s+\d+\s+\d+\s+([\d\.]+):(\d+)', line)
                    if match:
                        ports.append({
                            'ip': match.group(1),
                            'port': int(match.group(2))
                        })
            
            return ports
        except:
            return []
    
    def detect_suspicious_processes(self):
        """العمليات المريبة"""
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            suspicious = []
            for line in result.stdout.split('\n'):
                for proc in self.suspicious_processes:
                    if proc.lower() in line.lower():
                        parts = line.split()
                        if len(parts) >= 11:
                            suspicious.append({
                                'pid': parts[1],
                                'user': parts[0],
                                'command': ' '.join(parts[10:]),
                                'alert': f'⚠️ عملية مريبة: {proc}'
                            })
                        break
            
            return suspicious
        except:
            return []
    
    def monitor_file_changes(self, files=['/etc/passwd', '/etc/shadow', '/etc/ssh/sshd_config']):
        """مراقبة تغيير الملفات الحساسة"""
        try:
            changes = []
            for file in files:
                try:
                    result = subprocess.run(
                        ['md5sum', file],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if result.stdout:
                        hash_val = result.stdout.split()[0]
                        changes.append({
                            'file': file,
                            'hash': hash_val,
                            'timestamp': datetime.now().isoformat()
                        })
                except:
                    pass
            
            return changes
        except:
            return []
    
    def check_sudo_access(self):
        """من يستطيع استخدام sudo"""
        try:
            result = subprocess.run(
                ['grep', '-E', '^%?sudo', '/etc/sudoers'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return result.stdout.split('\n')
        except:
            return []
    
    def get_last_logins(self, lines=20):
        """آخر عمليات دخول"""
        try:
            result = subprocess.run(
                ['last', '-n', str(lines)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            logins = []
            for line in result.stdout.split('\n'):
                if line.strip() and 'still logged in' not in line.lower():
                    logins.append(line)
            
            return logins
        except:
            return []
    
    def check_firewall_status(self):
        """حالة جدار الحماية"""
        try:
            result = subprocess.run(
                ['sudo', 'ufw', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                'status': 'Active' if 'active' in result.stdout.lower() else 'Inactive',
                'details': result.stdout
            }
        except:
            return {'status': 'Unknown', 'details': 'UFW not available'}
