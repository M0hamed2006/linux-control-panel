from flask import Blueprint, jsonify, request, send_file
from services.export_manager import ExportManager
from services.database import Database
import os

export_bp = Blueprint('export', __name__, url_prefix='/api/export')
db = Database()

@export_bp.route('/stats/json', methods=['GET'])
def export_stats_json():
    """تصدير الإحصائيات JSON"""
    hours = request.args.get('hours', 24, type=int)
    stats = db.get_system_stats(hours)
    
    formatted = [
        {
            'timestamp': s[1],
            'cpu': s[2],
            'memory': s[3],
            'disk': s[4]
        } for s in stats
    ]
    
    filename = ExportManager.export_json(formatted)
    return jsonify({'filename': filename, 'exported': len(formatted)})

@export_bp.route('/stats/csv', methods=['GET'])
def export_stats_csv():
    """تصدير الإحصائيات CSV"""
    hours = request.args.get('hours', 24, type=int)
    stats = db.get_system_stats(hours)
    
    formatted = [
        {
            'timestamp': s[1],
            'cpu': s[2],
            'memory': s[3],
            'disk': s[4]
        } for s in stats
    ]
    
    filename = ExportManager.export_csv(formatted, ['timestamp', 'cpu', 'memory', 'disk'])
    return jsonify({'filename': filename, 'exported': len(formatted)})

@export_bp.route('/alerts/json', methods=['GET'])
def export_alerts():
    """تصدير التنبيهات"""
    alerts = db.get_alerts()
    
    formatted = [
        {
            'timestamp': a[1],
            'title': a[2],
            'message': a[3],
            'level': a[4]
        } for a in alerts
    ]
    
    filename = ExportManager.export_json(formatted)
    return jsonify({'filename': filename, 'exported': len(formatted)})

@export_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """تحميل الملف"""
    filepath = f"exports/{filename}"
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404
