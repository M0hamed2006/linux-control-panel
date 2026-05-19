from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit
from services.system_monitor import SystemMonitor
from services.alert_monitor import AlertMonitor
from services.database import Database
from services.performance_analyzer import PerformanceAnalyzer
from routes.dashboard import dashboard_bp
from routes.network import network_bp
from routes.security import security_bp
from routes.analytics import analytics_bp
import threading
import time

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'your-secret-key-here'

socketio = SocketIO(app, cors_allowed_origins="*")
monitor = SystemMonitor()
alert_monitor = AlertMonitor()
db = Database()
analyzer = PerformanceAnalyzer()

# تسجيل الـ Blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(network_bp)
app.register_blueprint(security_bp)
app.register_blueprint(analytics_bp)

monitoring = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('✅ Client connected')
    global monitoring
    monitoring = True
    emit('response', {'data': 'Connected to server'})
    
    thread = threading.Thread(target=send_system_data)
    thread.daemon = True
    thread.start()

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')
    global monitoring
    monitoring = False

def send_system_data():
    while monitoring:
        try:
            sys_data = monitor.get_all_system_info()
            
            # تسجيل المقاييس
            analyzer.record_metrics(
                sys_data['cpu']['percent'],
                sys_data['memory']['percent'],
                sys_data['disk']['percent']
            )
            
            alerts = alert_monitor.check_all(
                sys_data['cpu']['percent'],
                sys_data['memory']['percent'],
                sys_data['disk']['percent']
            )
            
            db.insert_system_stats(
                sys_data['cpu']['percent'],
                sys_data['memory']['percent'],
                sys_data['disk']['percent'],
                sys_data['network']['bytes_sent'],
                sys_data['network']['bytes_recv'],
                sys_data['process_count']
            )
            
            for alert in alerts:
                db.insert_alert(alert.title, alert.message, alert.level.value, alert.metric_type)
            
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

if __name__ == '__main__':
    print("🚀 Starting Linux Control Panel...")
    print("📱 Open http://localhost:5000 in your browser")
    socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=False)
