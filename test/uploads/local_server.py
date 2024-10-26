import asyncio
import websockets
import socket
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 配置WebSocket服务器
WEBSOCKET_PORT = 8765

# 配置UDP服务器
UDP_IP = "0.0.0.0"
UDP_PORT = 1206

# 创建Flask应用（用于API）
app = Flask(__name__)

# 创建UDP套接字
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

# 用于保存WebSocket客户端连接
connected_clients = set()

# 用于保存历史数据
sailing_data_history = []

async def udp_to_websocket():
    """
    接收UDP数据并通过WebSocket发送给所有连接的客户端，同时保存数据。
    """
    while True:
        data, addr = await asyncio.get_event_loop().run_in_executor(None, udp_sock.recvfrom, 1024)
        json_packet = data.decode('utf-8')
        parsed_data = json.loads(json_packet)
        print(f"Received JSON packet: {json_packet} from {addr}")
        
        # 保存历史数据
        sailing_data_history.append(parsed_data)
        
        # 将数据发送给所有WebSocket客户端
        if connected_clients:
            await asyncio.gather(
                *(client.send(json_packet) for client in connected_clients)
            )

async def websocket_handler(websocket, path):
    """
    处理WebSocket连接和断开。
    """
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message from WebSocket client: {message}")
    finally:
        connected_clients.remove(websocket)

# 提供API接口，获取历史数据
@app.route('/api/get_sailing_data', methods=['GET'])
def get_sailing_data():
    return jsonify(sailing_data_history)

# 提供控制模拟器的API（可扩展为其他功能）
@app.route('/api/control_simulator', methods=['POST'])
def control_simulator():
    command = request.json.get('command')
    if command == "start":
        return jsonify({"status": "simulator started"})
    elif command == "stop":
        return jsonify({"status": "simulator stopped"})
    else:
        return jsonify({"status": "unknown command"}), 400

async def start_websocket_server():
    """
    启动WebSocket服务器
    """
    websocket_server = await websockets.serve(websocket_handler, "0.0.0.0", WEBSOCKET_PORT)
    print(f"WebSocket server is running on port {WEBSOCKET_PORT}")
    await udp_to_websocket()
    await websocket_server.wait_closed()

if __name__ == '__main__':
    # 在一个线程中启动Flask API服务器
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    flask_thread.start()

    # 在主线程中运行WebSocket服务器
    asyncio.run(start_websocket_server())
