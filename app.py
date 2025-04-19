import os
import eventlet
import eventlet.wsgi
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, emit
from datetime import datetime
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app, async_mode='eventlet')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

rooms = {}  # {room_name: [messages]}
users = {}  # {sid: {'nickname': ..., 'room': ...}}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('join')
def handle_join(data):
    nickname = data['nickname']
    room = data['room']
    join_room(room)
    users[request.sid] = {'nickname': nickname, 'room': room}
    if room not in rooms:
        rooms[room] = []
    emit('system', {'msg': f"{nickname}님이 입장했습니다."}, room=room)
    emit('history', {'messages': rooms[room]}, room=request.sid)

@socketio.on('message')
def handle_message(data):
    room = users[request.sid]['room']
    nickname = users[request.sid]['nickname']
    msg = data['msg']
    timestamp = datetime.now().strftime('%H:%M:%S')
    message = {'nickname': nickname, 'msg': msg, 'timestamp': timestamp, 'type': 'text'}
    rooms[room].append(message)
    emit('message', message, room=room)

@socketio.on('emoji')
def handle_emoji(data):
    room = users[request.sid]['room']
    nickname = users[request.sid]['nickname']
    emoji = data['emoji']
    timestamp = datetime.now().strftime('%H:%M:%S')
    message = {'nickname': nickname, 'msg': emoji, 'timestamp': timestamp, 'type': 'emoji'}
    rooms[room].append(message)
    emit('message', message, room=room)

@socketio.on('file')
def handle_file(data):
    room = users[request.sid]['room']
    nickname = users[request.sid]['nickname']
    filedata = data['filedata']
    filename = secure_filename(data['filename'])
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'wb') as f:
        f.write(filedata)
    timestamp = datetime.now().strftime('%H:%M:%S')
    message = {'nickname': nickname, 'msg': f'/uploads/{filename}', 'timestamp': timestamp, 'type': 'file', 'filename': filename}
    rooms[room].append(message)
    emit('message', message, room=room)

@socketio.on('delete')
def handle_delete(data):
    room = users[request.sid]['room']
    idx = data['idx']
    nickname = users[request.sid]['nickname']
    # Only allow sender to delete their own message
    if rooms[room][idx]['nickname'] == nickname:
        del rooms[room][idx]
        emit('delete', {'idx': idx}, room=room)

@socketio.on('read')
def handle_read(data):
    room = users[request.sid]['room']
    idx = data['idx']
    nickname = users[request.sid]['nickname']
    # 메시지 읽음 처리
    if 'read_by' not in rooms[room][idx]:
        rooms[room][idx]['read_by'] = []
    if nickname not in rooms[room][idx]['read_by']:
        rooms[room][idx]['read_by'].append(nickname)
    emit('read', {'idx': idx, 'read_by': rooms[room][idx]['read_by']}, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit('system', {'msg': f"{user['nickname']}님이 퇴장했습니다."}, room=user['room'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port)
