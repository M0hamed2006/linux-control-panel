import subprocess
import re
import json
import socket
from datetime import datetime
import threading
import time
from collections import defaultdict

class NetworkScanner:
    """خدمة مراقبة الشبكة والأجهزة"""
    
    def __init__(self):
        self.discovered_devices = {}
        self.network_history = []
        self.arp_table = {}
        self.suspicious_ips = set()
        self.lock = threading.Lock()
    
    # ==================== WiFi Scanning ====================
    
    @staticmethod
    def scan_wifi_networks():
        """مسح شبكات الواي فاي المتاحة"""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,CHAN', 'device', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            networks = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if line.strip():
                    parts = line.split(':')
                    if len(parts) >= 4:
                        networks.append({
                            'ssid': parts[0] if parts[0] else '[HIDDEN]',
                            'signal': int(parts[1]) if parts[1].isdigit() else 0,
                            'security': parts[2] if parts[2] else 'Open',
                            'channel': parts[3] if parts[3] else 'N/A',
                            'timestamp': datetime.now().isoformat()
                        })
            
            return sorted(networks, key=lambda x: x['signal'], reverse=True)
        except Exception as e:
            print(f"WiFi Scan Error: {e}")
            return []
    
    @staticmethod
    def get_current_wifi():
        """الاتصال الحالي بالواي فاي"""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,TYPE,DEVICE,STATE', 'connection', 'show', '--active'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split(':')
                    if len(parts) >= 4 and 'wifi' in parts[1].lower():
                        return {
                            'name': parts[0],
                            'type': parts[1],
                            'device': parts[2],
                            'state': parts[3]
                        }
            
            return None
        except Exception as e:
            print(f"Current WiFi Error: {e}")
            return None
    
    # ==================== Device Discovery ====================
    
    @staticmethod
    def discover_devices():
        """اكتشاف الأجهزة على الشبكة المحلية"""
        try:
            result = subprocess.run(
                ['nmap', '-sn', '-PR', '192.168.1.0/24'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            devices = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'Nmap scan report' in line:
                    ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip:
                        devices.append({'ip': ip.group(1)})
            
            return devices
        except Exception as e:
            print(f"Device Discovery Error: {e}")
            return []
    
    @staticmethod
    def get_arp_table():
        """الحصول على جدول ARP"""
        try:
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            devices = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                match = re.search(r'(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F:]{17})', line)
                if match:
                    devices.append({
                        'ip': match.group(1),
                        'mac': match.group(2),
                        'timestamp': datetime.now().isoformat()
                    })
            
            return devices
        except Exception as e:
            print(f"ARP Table Error: {e}")
            return []
    
    @staticmethod
    def get_vendor_by_mac(mac):
        """الحصول على شركة المصنع من MAC address"""
        try:
            # تبسيط - يمكن استخدام macvendors API
            mac_prefix = mac[:8].upper()
            
            # قاعدة بيانات بسيطة
            vendors = {
                '00:0A:95': 'Netgear',
                '00:1A:2F': 'Cisco',
                '00:25:86': 'Apple',
                '28:6E:D2': 'TP-Link',
                'B4:2E:99': 'Xiaomi',
                'AC:9E:17': 'Samsung',
                'F0:21:65': 'OnePlus',
            }
            
            for prefix, vendor in vendors.items():
                if mac.upper().startswith(prefix):
                    return vendor
            
            return 'Unknown'
        except Exception as e:
            return 'Unknown'
    
    # ==================== Port Scanning ====================
    
    @staticmethod
    def scan_ports(ip, ports='1-1000'):
        """فحص المنافذ المفتوحة"""
        try:
            result = subprocess.run(
                ['nmap', '-p', ports, ip],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            open_ports = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'open' in line.lower():
                    match = re.search(r'(\d+)/tcp\s+open\s+(\w+)', line)
                    if match:
                        open_ports.append({
                            'port': int(match.group(1)),
                            'service': match.group(2)
                        })
            
            return open_ports
        except Exception as e:
            print(f"Port Scan Error: {e}")
            return []
    
    @staticmethod
    def quick_port_scan(ip, timeout=2):
        """فحص سريع للمنافذ الشهيرة"""
        common_ports = [22, 80, 443, 3306, 5432, 8080, 8443]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
            except Exception:
                pass
        
        return open_ports
    
    # ==================== DNS Tools ====================
    
    @staticmethod
    def dns_lookup(domain):
        """DNS lookup"""
        try:
            ip = socket.gethostbyname(domain)
            return {'domain': domain, 'ip': ip}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def reverse_dns(ip):
        """Reverse DNS lookup"""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return {'ip': ip, 'hostname': hostname}
        except Exception as e:
            return {'error': str(e)}
    
    # ==================== Ping & Traceroute ====================
    
    @staticmethod
    def ping_host(ip):
        """Ping جهاز"""
        try:
            result = subprocess.run(
                ['ping', '-c', '4', ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # استخراج الإحصائيات
                match = re.search(r'(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)', result.stdout)
                if match:
                    return {
                        'status': 'Online',
                        'min': float(match.group(1)),
                        'avg': float(match.group(2)),
                        'max': float(match.group(3))
                    }
                return {'status': 'Online'}
            else:
                return {'status': 'Offline'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def traceroute(ip):
        """Traceroute"""
        try:
            result = subprocess.run(
                ['traceroute', '-m', '15', ip],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            hops = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if '*' not in line and line.strip():
                    match = re.search(r'^\s*(\d+)\s+([\w\-\.]+)\s+\(([\d\.]+)\)', line)
                    if match:
                        hops.append({
                            'hop': int(match.group(1)),
                            'hostname': match.group(2),
                            'ip': match.group(3)
                        })
            
            return {'hops': hops}
        except Exception as e:
            return {'error': str(e)}
    
    # ==================== Ping Sweep ====================
    
    @staticmethod
    def ping_sweep(network='192.168.1.0/24', threads=10):
        """مسح سريع للـ IPs"""
        import ipaddress
        from concurrent.futures import ThreadPoolExecutor
        
        try:
            net = ipaddress.ip_network(network, strict=False)
            results = []
            
            def ping_single(ip):
                try:
                    result = subprocess.run(
                        ['ping', '-c', '1', str(ip)],
                        capture_output=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        return {'ip': str(ip), 'status': 'Online'}
                except:
                    pass
                return None
            
            with ThreadPoolExecutor(max_workers=threads) as executor:
                for result in executor.map(ping_single, net.hosts()):
                    if result:
                        results.append(result)
            
            return results
        except Exception as e:
            print(f"Ping Sweep Error: {e}")
            return []
    
    # ==================== ARP Spoofing Detection ====================
    
    def detect_arp_spoofing(self):
        """كشف هجمات ARP spoofing"""
        try:
            current_arp = self.get_arp_table()
            suspicions = []
            
            for entry in current_arp:
                ip = entry['ip']
                mac = entry['mac']
                
                if ip in self.arp_table:
                    if self.arp_table[ip] != mac:
                        suspicions.append({
                            'ip': ip,
                            'old_mac': self.arp_table[ip],
                            'new_mac': mac,
                            'alert': 'ARP Spoofing Detected!'
                        })
                
                self.arp_table[ip] = mac
            
            return suspicions
        except Exception as e:
            print(f"ARP Detection Error: {e}")
            return []
    
    # ==================== Network Interface Info ====================
    
    @staticmethod
    def get_network_interfaces():
        """معلومات التوصيلات"""
        try:
            result = subprocess.run(
                ['nmcli', 'device', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            interfaces = []
            lines = result.stdout.split('\n')[1:]  # تخطي الرأس
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        interfaces.append({
                            'device': parts[0],
                            'type': parts[1],
                            'state': parts[2],
                            'connection': parts[3] if len(parts) > 3 else 'N/A'
                        })
            
            return interfaces
        except Exception as e:
            print(f"Network Interfaces Error: {e}")
            return []
