from flask import Flask, render_template
from flask_socketio import SocketIO
import os

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'your-secret-key-here'

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('response', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("Starting Linux Control Panel...")
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
