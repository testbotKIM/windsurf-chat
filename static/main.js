let socket;
function join() {
    const nickname = document.getElementById('nickname').value;
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
        div.innerHTML += `<a href="${obj.msg}" target="_blank">${obj.filename}</a>`;
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
