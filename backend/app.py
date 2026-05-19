from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from services.system_monitor import SystemMonitor
from services.alert_monitor import AlertMonitor
from services.database import Database
from routes.dashboard import dashboard_bp
import threading
import time

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'your-secret-key-here'

socketio = SocketIO(app, cors_allowed_origins="*")
monitor = SystemMonitor()
alert_monitor = AlertMonitor()
db = Database()

# تسجيل الـ Blueprint
app.register_blueprint(dashboard_bp)

# متغير للتحكم في الـ Thread
monitoring = False
last_alert_state = {}

@app.route('/')
def index():
    return render_template('index.html')

# الاتصال بالعميل
@socketio.on('connect')
def handle_connect():
    print('✅ Client connected')
    global monitoring
    monitoring = True
    emit('response', {'data': 'Connected to server'})
    
    # بدء الـ monitoring thread
    thread = threading.Thread(target=send_system_data)
    thread.daemon = True
    thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')
    global monitoring
    monitoring = False

def send_system_data():
    """بث البيانات كل ثانية للعميل"""
    while monitoring:
        try:
            sys_data = monitor.get_all_system_info()
            
            # فحص التنبيهات
            alerts = alert_monitor.check_all(
                sys_data['cpu']['percent'],
                sys_data['memory']['percent'],
                sys_data['disk']['percent']
            )
            
            # حفظ البيانات في قاعدة البيانات
            db.insert_system_stats(
                sys_data['cpu']['percent'],
                sys_data['memory']['percent'],
                sys_data['disk']['percent'],
                sys_data['network']['bytes_sent'],
                sys_data['network']['bytes_recv'],
                sys_data['process_count']
            )
            
            # حفظ التنبيهات في قاعدة البيانات
            for alert in alerts:
                db.insert_alert(alert.title, alert.message, alert.level.value, alert.metric_type)
            
            # بث البيانات
            data = {
                'cpu': sys_data['cpu'],
                'memory': sys_data['memory'],
                'disk': sys_data['disk'],
                'network': sys_data['network'],
                'process_count': sys_data['process_count'],
                'uptime': sys_data['uptime'],
                'timestamp': time.time(),
                'alerts': [a.to_dict() for a in alerts] if alerts else [],
                'unread_alerts': alert_monitor.get_unread_count()
            }
            
            socketio.emit('system_data', data, broadcast=True)
            time.sleep(1)
        except Exception as e:
            print(f'Error: {e}')
            time.sleep(1)

# Alerts API
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    from flask import request, jsonify
    limit = request.args.get('limit', 50, type=int)
    alerts = alert_monitor.get_alerts(limit)
    return jsonify({'alerts': alerts})

@app.route('/api/alerts/unread', methods=['GET'])
def get_unread_alerts():
    from flask import jsonify
    count = alert_monitor.get_unread_count()
    return jsonify({'unread_count': count})

@app.route('/api/alerts/thresholds', methods=['GET'])
def get_thresholds():
    from flask import jsonify
    thresholds = alert_monitor.get_thresholds()
    return jsonify({'thresholds': thresholds})

@app.route('/api/alerts/thresholds', methods=['POST'])
def set_thresholds():
    from flask import request, jsonify
    data = request.json
    metric = data.get('metric')
    level = data.get('level')
    value = data.get('value')
    
    success = alert_monitor.set_threshold(metric, level, value)
    db.set_setting(f'threshold_{metric}_{level}', str(value))
    
    return jsonify({'success': success})

# Statistics API
@app.route('/api/stats/history', methods=['GET'])
def get_stats_history():
    from flask import request, jsonify
    hours = request.args.get('hours', 24, type=int)
    stats = db.get_system_stats(hours)
    
    formatted_stats = []
    for stat in stats:
        formatted_stats.append({
            'timestamp': stat[1],
            'cpu': stat[2],
            'memory': stat[3],
            'disk': stat[4],
            'network_sent': stat[5],
            'network_recv': stat[6],
            'process_count': stat[7]
        })
    
    return jsonify({'stats': formatted_stats})

if __name__ == '__main__':
    print("🚀 Starting Linux Control Panel...")
    print("📱 Open http://localhost:5000 in your browser")
    socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=False)
