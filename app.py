from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
import jwt
import bcrypt
import json
from database import db
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ===================== احراز هویت =====================
def verify_token(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return payload.get('user_id')
    except:
        return None

def login_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# ===================== صفحات =====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.json.get('password')
        if password == Config.ADMIN_PASSWORD:
            token = jwt.encode({
                'user_id': 'admin',
                'exp': datetime.utcnow() + timedelta(days=1)
            }, Config.JWT_SECRET)
            return jsonify({'token': token})
        return jsonify({'error': 'Invalid password'}), 401
    return render_template('login.html')

# ===================== API ها =====================
@app.route('/api/stats')
@login_required
def get_stats():
    return jsonify(db.get_stats())

@app.route('/api/users')
@login_required
def get_users():
    return jsonify(db.get_all_users())

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    data = request.json
    user = db.create_user(
        name=data.get('name'),
        traffic_limit=data.get('traffic_limit', 10),
        expiry_days=data.get('expiry_days', 30)
    )
    return jsonify(user)

@app.route('/api/users/<user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if db.delete_user(user_id):
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/users/<user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    user = db.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    user.update(data)
    db.save()
    return jsonify({'success': True})

@app.route('/api/inbounds')
@login_required
def get_inbounds():
    return jsonify(db.data['inbounds'])

@app.route('/api/inbounds', methods=['POST'])
@login_required
def create_inbound():
    data = request.json
    inbound_id = f"inbound_{datetime.now().timestamp()}"
    db.data['inbounds'][inbound_id] = data
    db.save()
    return jsonify({'id': inbound_id, **data})

# ===================== وب‌سوکت =====================
@socketio.on('connect')
def handle_connect():
    emit('message', {'data': 'Connected to server'})

@socketio.on('get_live_traffic')
def handle_live_traffic():
    # شبیه‌سازی ترافیک زنده
    import random
    while True:
        emit('traffic_update', {
            'inbound': random.randint(10, 100),
            'outbound': random.randint(10, 100),
            'timestamp': datetime.now().isoformat()
        })
        socketio.sleep(2)

# ===================== اجرا =====================
if __name__ == '__main__':
    print("🚀 X-Panel در حال اجرا...")
    print(f"📡 آدرس: http://localhost:{Config.SERVER_PORT}")
    socketio.run(app, host=Config.SERVER_IP, port=Config.SERVER_PORT, debug=True)
