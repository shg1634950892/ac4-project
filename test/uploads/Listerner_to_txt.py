import socket
import threading
import logging
import sys
import json
from flask import Flask, jsonify
from flask_cors import CORS  # 引入 CORS 支持
from flask_socketio import SocketIO
from analysinglargerpackets import parse_extended_binary_data  # 导入解析函数
from api_routes import setup_api_routes  # 导入 API 路由

# Flask and SocketIO setup
app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)  # 允许跨域请求
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许所有来源的跨域请求

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("simulation_data.log"),
    logging.StreamHandler(sys.stdout)
])

# Use "0.0.0.0" to listen on all available network interfaces
LOCAL_UDP_IP = "0.0.0.0"
LOCAL_UDP_PORT = 1206  # Port for UDP data

# 保存数据到JSON文件
def save_data_to_file(data, file_path='sailing_data.json'):
    with open(file_path, 'a') as f:
        json.dump(data, f)
        f.write('\n')  # 每次写入后换行保存

# WebSocket event to send data to all connected clients
def send_data_via_websocket(data):
    """
    Emit the parsed sailing data to all connected WebSocket clients.
    """
    socketio.emit('sailing_data', data)
    logging.info(f"Data sent via WebSocket: {data}")

def process_packet(packet):
    """Process the received packet, parse it, log its contents, then push via WebSocket."""
    try:
        # Convert binary data to hexadecimal (for logging/debugging)
        hex_data = packet.hex()
        logging.info(f"Raw data (hex): {hex_data}")

        # Call the parsing function to convert binary data into structured format
        parsed_data = parse_extended_binary_data(packet)
        
        if parsed_data:
            logging.info(f"Parsed data: {parsed_data}")
            # Send parsed data via WebSocket
            send_data_via_websocket(parsed_data)

            # 保存数据到文件
            save_data_to_file(parsed_data)

        else:
            logging.warning("Failed to parse data packet")
    except Exception as e:
        logging.error(f"Error processing packet: {e}")

def listen_for_udp_data():
    """Function to listen for UDP data on the specified port and process it."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((LOCAL_UDP_IP, LOCAL_UDP_PORT))  # Bind to local IP and port to listen for incoming UDP data
    logging.info(f"Listening for UDP data on {LOCAL_UDP_IP}:{LOCAL_UDP_PORT}...")

    while True:
        try:
            # Receive data from UDP
            packet, addr = udp_socket.recvfrom(4096)  # Adjust buffer size as needed
            logging.info(f"Received {len(packet)} bytes from {addr} (UDP)")

            # Process the packet
            process_packet(packet)
        except Exception as e:
            logging.error(f"Error receiving UDP data: {e}")

# 注册API路由
setup_api_routes(app)

# WebSocket route for client connections
@app.route('/')
def index():
    return "WebSocket server is running!"

def start_udp_listener():
    """Start the UDP listener in a separate thread."""
    udp_thread = threading.Thread(target=listen_for_udp_data)
    udp_thread.daemon = True  # Make sure the thread exits when the main program does
    udp_thread.start()

if __name__ == '__main__':  
    # Start UDP listener thread
    start_udp_listener()

    # Run Flask app with SocketIO for WebSocket communication
    socketio.run(app, host='0.0.0.0', port=5000)







