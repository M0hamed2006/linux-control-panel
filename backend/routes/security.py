from flask import Blueprint, jsonify
from services.security_monitor import SecurityMonitor

security_bp = Blueprint('security', __name__, url_prefix='/api/security')
monitor = SecurityMonitor()

@security_bp.route('/failed-logins', methods=['GET'])
def get_failed_logins():
    """محاولات الدخول الفاشلة"""
    attempts = monitor.get_failed_login_attempts()
    return jsonify({'attempts': attempts})

@security_bp.route('/brute-force-detection', methods=['GET'])
def detect_brute_force():
    """كشف brute force"""
    suspicious = monitor.detect_brute_force()
    return jsonify({'suspicious': suspicious, 'count': len(suspicious)})

@security_bp.route('/open-ports', methods=['GET'])
def get_open_ports():
    """المنافذ المفتوحة"""
    ports = monitor.get_open_ports()
    return jsonify({'ports': ports})

@security_bp.route('/suspicious-processes', methods=['GET'])
def get_suspicious_processes():
    """العمليات المريبة"""
    processes = monitor.detect_suspicious_processes()
    return jsonify({'processes': processes})

@security_bp.route('/file-changes', methods=['GET'])
def check_file_changes():
    """تغييرات الملفات"""
    changes = monitor.monitor_file_changes()
    return jsonify({'changes': changes})

@security_bp.route('/last-logins', methods=['GET'])
def get_last_logins():
    """آخر عمليات دخول"""
    logins = monitor.get_last_logins()
    return jsonify({'logins': logins})

@security_bp.route('/firewall', methods=['GET'])
def firewall_status():
    """حالة الفايروول"""
    status = monitor.check_firewall_status()
    return jsonify(status)
