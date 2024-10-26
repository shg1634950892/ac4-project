from flask import Flask, render_template
import os
import json
from flask_socketio import SocketIO
import socket
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许所有来源的跨域请求
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 二进制文件转 JSON 示例函数
def spb_to_json(spb_file_path):
    data = []

    # 逐行读取文件
    with open(spb_file_path, 'r', encoding='utf-8') as spb_file:
        for line in spb_file:
            clean_line = line.strip()  # 去掉行首尾的空格和换行符

            if clean_line:
                row = clean_line.split()  # 按空格或制表符分割

                # 尝试将数据转换为浮点数或整数
                parsed_row = []
                for value in row:
                    try:
                        parsed_value = float(value) if '.' in value else int(value)
                    except ValueError:
                        parsed_value = value
                    parsed_row.append(parsed_value)

                data.append(parsed_row)

    json_data = json.dumps(data, indent=4)
    return json_data

# 上传文件路由
@app.route('/')
def upload_form():
    return render_template('upload.html')

# 处理文件上传
@socketio.on('send_file')
def handle_file(data):
    try:
        file_data = data['file']
        filename = data['filename']
        
        if not filename.endswith('.spb'):
            socketio.emit('file_received', {'message': 'Invalid file type! Only .spb files are allowed.'})
            return

        # 保存接收到的二进制文件
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(file_path, 'wb') as f:
            f.write(file_data.encode('latin1'))

        # 转换 .spb 文件为 JSON
        json_data = spb_to_json(file_path)

        # 保存 JSON 文件
        json_filename = filename.rsplit('.', 1)[0] + '.json'
        json_file_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        
        with open(json_file_path, 'w') as json_file:
            json_file.write(json_data)

        preview = file_data[:100]  # 显示前100字节内容作为预览
        socketio.emit('file_received', {
            'message': f'{filename} successfully uploaded and converted to {json_filename}',
            'preview': preview
        })
    except Exception as e:
        socketio.emit('file_received', {'message': f'Error: {str(e)}'})

# UDP 数据监听器
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

def udp_listener():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP data on {UDP_IP}:{UDP_PORT}")

    while True:
        data, addr = udp_sock.recvfrom(1024)  # 接收1024字节的数据
        print(f"Received data from {addr}: {data}")
        socketio.emit('udp_data', {'data': data.decode('utf-8')})

# 启动 UDP 监听器线程
if __name__ == "__main__":
    udp_thread = threading.Thread(target=udp_listener)
    udp_thread.daemon = True  # 守护线程，当主线程退出时，UDP线程自动终止
    udp_thread.start()

    # 启动 Flask-SocketIO 应用，注意此处更改了 Flask 的端口，避免与 UDP 监听端口冲突
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)  # 使用5000端口











