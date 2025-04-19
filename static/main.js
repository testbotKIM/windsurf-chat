function backToRoomList() {
    document.getElementById('chat').style.display = 'none';
    document.getElementById('roomListView').style.display = 'block';
    document.getElementById('login').style.display = 'none';
    // 필요하다면 소켓 연결 해제 등 추가 작업 가능
}
window.backToRoomList = backToRoomList;

let socket;
function createRoom() {
    const nickname = document.getElementById('nickname').value;
    if (!nickname) {
        alert('닉네임을 입력하세요!');
        return;
    }
    // 방 이름 입력 UI로 전환
    document.getElementById('roomListView').style.display = 'none';
    document.getElementById('login').style.display = 'block';
    // 닉네임 값을 다음 단계(join)에서 쓸 수 있도록 login 영역에도 표시(필요시)
    document.getElementById('login-nickname').value = nickname;
}
window.createRoom = createRoom;

function join() {
    const nickname = document.getElementById('login-nickname').value;
    const room = document.getElementById('room').value;
    if (!nickname || !room) return alert('닉네임/방이름 입력');
    document.getElementById('login').style.display = 'none';
    document.getElementById('chat').style.display = 'block';
    socket = io();
    socket.emit('join', {nickname, room});
    socket.on('system', data => addMsg('system', data.msg));
    socket.on('history', data => data.messages.forEach(addMsgFromObj));
    socket.on('message', addMsgFromObj);
    socket.on('delete', data => document.getElementById('msg'+data.idx)?.remove());
    socket.on('read', data => {/* 읽음 표시 갱신 */});
}
function sendMsg() {
    const msg = document.getElementById('msg').value;
    if (msg) socket.emit('message', {msg});
    document.getElementById('msg').value = '';
}
// 메시지 입력창에서 Enter 키로 메시지 전송
const msgInput = document.getElementById('msg');
if (msgInput) {
    msgInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            sendMsg();
        }
    });
}

function sendEmoji(emoji) {
    socket.emit('emoji', {emoji});
}
function addMsg(role, msg) {
    const div = document.createElement('div');
    div.className = role;
    div.innerText = msg;
    document.getElementById('messages').appendChild(div);
}
function addMsgFromObj(obj, idx) {
    const div = document.createElement('div');
    div.id = 'msg'+idx;
    div.innerHTML = `<b>${obj.nickname}</b> [${obj.timestamp}]: `;
    if (obj.type === 'file') {
        // 이미지 확장자면 미리보기, 아니면 링크
        const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(obj.filename);
        if (isImage) {
            div.innerHTML += `<img src="${obj.msg}" alt="${obj.filename}" style="max-width:150px; max-height:150px; cursor:pointer; border:1px solid #ccc; margin:5px 0;" onclick="window.open('${obj.msg}','_blank')">`;
        } else {
            div.innerHTML += `<a href="${obj.msg}" target="_blank">${obj.filename}</a>`;
        }
    } else {
        div.innerHTML += obj.msg;
    }
    document.getElementById('messages').appendChild(div);
}
document.getElementById('fileInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = function(evt) {
        socket.emit('file', {filename: file.name, filedata: evt.target.result});
    };
    reader.readAsArrayBuffer(file);
});
