from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from services.system_monitor import SystemMonitor
import threading
import time

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'your-secret-key-here'

socketio = SocketIO(app, cors_allowed_origins="*")
monitor = SystemMonitor()

# متغير للتحكم في الـ Thread
monitoring = False

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
            data = {
                'cpu': monitor.get_cpu_info(),
                'memory': monitor.get_memory_info(),
                'disk': monitor.get_disk_info(),
                'network': monitor.get_network_info(),
                'process_count': monitor.get_process_count(),
                'uptime': monitor.get_uptime(),
                'timestamp': time.time()
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
