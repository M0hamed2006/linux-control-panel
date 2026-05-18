from flask import Blueprint, jsonify, request
from services.system_monitor import SystemMonitor
from services.process_monitor import ProcessMonitor
from services.service_monitor import ServiceMonitor
from services.log_monitor import LogMonitor

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

system_monitor = SystemMonitor()
process_monitor = ProcessMonitor()
service_monitor = ServiceMonitor()
log_monitor = LogMonitor()

# ==================== System Endpoints ====================

@dashboard_bp.route('/system-info', methods=['GET'])
def get_system_info():
    """الحصول على معلومات النظام"""
    return jsonify(system_monitor.get_all_system_info())

@dashboard_bp.route('/process-count', methods=['GET'])
def get_process_count():
    """عدد العمليات"""
    return jsonify({'process_count': system_monitor.get_process_count()})

@dashboard_bp.route('/network-info', methods=['GET'])
def get_network_info():
    """معلومات الشبكة"""
    return jsonify(system_monitor.get_network_info())

# ==================== Process Endpoints ====================

@dashboard_bp.route('/processes/top', methods=['GET'])
def get_top_processes():
    """أعلى العمليات استهلاكاً"""
    n = request.args.get('n', 10, type=int)
    sort_by = request.args.get('sort_by', 'cpu')
    processes = process_monitor.get_top_processes(n, sort_by)
    return jsonify({'processes': processes})

@dashboard_bp.route('/processes/all', methods=['GET'])
def get_all_processes():
    """كل العمليات"""
    processes = process_monitor.get_all_processes()
    return jsonify({'processes': processes})

@dashboard_bp.route('/process/<int:pid>', methods=['GET'])
def get_process_details(pid):
    """تفاصيل عملية معينة"""
    details = process_monitor.get_process_details(pid)
    return jsonify(details)

@dashboard_bp.route('/process/<int:pid>/kill', methods=['POST'])
def kill_process(pid):
    """إيقاف عملية"""
    result = process_monitor.kill_process(pid)
    return jsonify(result)

# ==================== Service Endpoints ====================

@dashboard_bp.route('/services/all', methods=['GET'])
def get_all_services():
    """كل الخدمات"""
    services = service_monitor.get_all_services()
    return jsonify({'services': services})

@dashboard_bp.route('/service/<service_name>/status', methods=['GET'])
def get_service_status(service_name):
    """حالة خدمة معينة"""
    status = service_monitor.get_service_status(service_name)
    return jsonify(status)

@dashboard_bp.route('/service/<service_name>/start', methods=['POST'])
def start_service(service_name):
    """تشغيل خدمة"""
    result = service_monitor.start_service(service_name)
    return jsonify(result)

@dashboard_bp.route('/service/<service_name>/stop', methods=['POST'])
def stop_service(service_name):
    """إيقاف خدمة"""
    result = service_monitor.stop_service(service_name)
    return jsonify(result)

@dashboard_bp.route('/service/<service_name>/restart', methods=['POST'])
def restart_service(service_name):
    """إعادة تشغيل خدمة"""
    result = service_monitor.restart_service(service_name)
    return jsonify(result)

@dashboard_bp.route('/service/<service_name>/enable', methods=['POST'])
def enable_service(service_name):
    """تفعيل خدمة"""
    result = service_monitor.enable_service(service_name)
    return jsonify(result)

@dashboard_bp.route('/service/<service_name>/disable', methods=['POST'])
def disable_service(service_name):
    """تعطيل خدمة"""
    result = service_monitor.disable_service(service_name)
    return jsonify(result)

# ==================== Log Endpoints ====================

@dashboard_bp.route('/logs/<log_type>', methods=['GET'])
def get_logs(log_type):
    """قراءة ملف log"""
    lines = request.args.get('lines', 50, type=int)
    logs = log_monitor.get_log_file(log_type, lines)
    return jsonify(logs)

@dashboard_bp.route('/logs/errors', methods=['GET'])
def get_errors():
    """آخر الأخطاء"""
    lines = request.args.get('lines', 20, type=int)
    errors = log_monitor.get_recent_errors(lines)
    return jsonify(errors)

@dashboard_bp.route('/logs/warnings', methods=['GET'])
def get_warnings():
    """آخر التحذيرات"""
    lines = request.args.get('lines', 20, type=int)
    warnings = log_monitor.get_recent_warnings(lines)
    return jsonify(warnings)

@dashboard_bp.route('/logs/search', methods=['GET'])
def search_logs():
    """البحث في الـ logs"""
    keyword = request.args.get('keyword', '')
    log_type = request.args.get('type', 'system')
    lines = request.args.get('lines', 50, type=int)
    
    if not keyword:
        return jsonify({'error': 'keyword is required'}), 400
    
    results = log_monitor.search_logs(keyword, log_type, lines)
    return jsonify(results)

@dashboard_bp.route('/logs/failed-logins', methods=['GET'])
def get_failed_logins():
    """محاولات تسجيل دخول فاشلة"""
    attempts = log_monitor.get_failed_login_attempts()
    return jsonify(attempts)

@dashboard_bp.route('/logs/sudo', methods=['GET'])
def get_sudo_logs():
    """أوامر sudo"""
    lines = request.args.get('lines', 20, type=int)
    commands = log_monitor.get_sudo_commands(lines)
    return jsonify(commands)

@dashboard_bp.route('/logs/disk-space', methods=['GET'])
def get_disk_space_logs():
    """تحذيرات مساحة القرص"""
    logs = log_monitor.get_disk_space_logs()
    return jsonify(logs)
