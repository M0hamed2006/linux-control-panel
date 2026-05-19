from flask import Blueprint, jsonify
from services.performance_analyzer import PerformanceAnalyzer

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')
analyzer = PerformanceAnalyzer()

@analytics_bp.route('/report', methods=['GET'])
def get_report():
    """تقرير الأداء الشامل"""
    report = analyzer.get_report()
    return jsonify(report)

@analytics_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """الشذوذ المكتشفة"""
    anomalies = analyzer.detect_anomalies()
    return jsonify({'anomalies': anomalies})

@analytics_bp.route('/trends', methods=['GET'])
def get_trends():
    """الاتجاهات"""
    return jsonify({
        'cpu': analyzer.get_trend('cpu'),
        'memory': analyzer.get_trend('memory'),
        'disk': analyzer.get_trend('disk')
    })

@analytics_bp.route('/cpu/average', methods=['GET'])
def cpu_average():
    """متوسط CPU"""
    return jsonify({'average': analyzer.get_average_cpu()})

@analytics_bp.route('/memory/average', methods=['GET'])
def memory_average():
    """متوسط Memory"""
    return jsonify({'average': analyzer.get_average_memory()})
