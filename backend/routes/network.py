from flask import Blueprint, jsonify, request
from services.network_scanner import NetworkScanner

network_bp = Blueprint('network', __name__, url_prefix='/api/network')
scanner = NetworkScanner()

# ==================== WiFi ====================

@network_bp.route('/wifi/scan', methods=['GET'])
def scan_wifi():
    """مسح الشبكات"""
    networks = scanner.scan_wifi_networks()
    return jsonify({'networks': networks})

@network_bp.route('/wifi/current', methods=['GET'])
def get_current_wifi():
    """الاتصال الحالي"""
    current = scanner.get_current_wifi()
    return jsonify({'current': current})

# ==================== Devices ====================

@network_bp.route('/devices/discover', methods=['GET'])
def discover_devices():
    """اكتشاف الأجهزة"""
    devices = scanner.discover_devices()
    return jsonify({'devices': devices})

@network_bp.route('/devices/arp', methods=['GET'])
def get_arp_table():
    """جدول ARP"""
    arp = scanner.get_arp_table()
    
    # إضافة معلومات الشركة
    for entry in arp:
        entry['vendor'] = scanner.get_vendor_by_mac(entry['mac'])
    
    return jsonify({'devices': arp})

# ==================== Port Scanning ====================

@network_bp.route('/ports/scan', methods=['POST'])
def scan_ports():
    """فحص المنافذ"""
    data = request.json
    ip = data.get('ip')
    ports = data.get('ports', '1-1000')
    
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    open_ports = scanner.scan_ports(ip, ports)
    return jsonify({'ip': ip, 'open_ports': open_ports})

@network_bp.route('/ports/quick', methods=['POST'])
def quick_port_scan():
    """فحص سريع"""
    data = request.json
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    open_ports = scanner.quick_port_scan(ip)
    return jsonify({'ip': ip, 'open_ports': open_ports})

# ==================== DNS ====================

@network_bp.route('/dns/lookup', methods=['POST'])
def dns_lookup():
    """DNS lookup"""
    data = request.json
    domain = data.get('domain')
    
    if not domain:
        return jsonify({'error': 'Domain required'}), 400
    
    result = scanner.dns_lookup(domain)
    return jsonify(result)

@network_bp.route('/dns/reverse', methods=['POST'])
def reverse_dns():
    """Reverse DNS"""
    data = request.json
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    result = scanner.reverse_dns(ip)
    return jsonify(result)

# ==================== Ping & Traceroute ====================

@network_bp.route('/ping', methods=['POST'])
def ping():
    """Ping"""
    data = request.json
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    result = scanner.ping_host(ip)
    return jsonify({'ip': ip, **result})

@network_bp.route('/traceroute', methods=['POST'])
def traceroute():
    """Traceroute"""
    data = request.json
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    result = scanner.traceroute(ip)
    return jsonify({'ip': ip, **result})

@network_bp.route('/ping-sweep', methods=['POST'])
def ping_sweep():
    """Ping Sweep"""
    data = request.json
    network = data.get('network', '192.168.1.0/24')
    
    results = scanner.ping_sweep(network)
    return jsonify({'network': network, 'online_hosts': results})

# ==================== Interfaces ====================

@network_bp.route('/interfaces', methods=['GET'])
def get_interfaces():
    """معلومات الاتصالات"""
    interfaces = scanner.get_network_interfaces()
    return jsonify({'interfaces': interfaces})

# ==================== ARP Detection ====================

@network_bp.route('/arp/spoofing', methods=['GET'])
def detect_arp_spoofing():
    """كشف ARP spoofing"""
    suspicions = scanner.detect_arp_spoofing()
    return jsonify({'suspicions': suspicions, 'count': len(suspicions)})
