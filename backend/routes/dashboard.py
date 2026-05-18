from flask import Blueprint, jsonify
import psutil

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

@dashboard_bp.route('/system-info', methods=['GET'])
def get_system_info():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        data = {
            'cpu': cpu_percent,
            'memory': {
                'percent': memory.percent,
                'used': memory.used / (1024**3),
                'total': memory.total / (1024**3)
            },
            'disk': {
                'percent': disk.percent,
                'used': disk.used / (1024**3),
                'total': disk.total / (1024**3)
            },
            'uptime': psutil.boot_time()
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/process-count', methods=['GET'])
def get_process_count():
    try:
        count = len(psutil.pids())
        return jsonify({'process_count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/network-info', methods=['GET'])
def get_network_info():
    try:
        net_io = psutil.net_io_counters()
        data = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
