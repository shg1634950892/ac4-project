import socket
import time
import json

# 设置本地UDP服务器的IP地址和端口
UDP_IP = "localhost"
UDP_PORT = 1206  # 和你的服务器监听的端口保持一致

# 使用实际路径读取JSON文件
json_file_path = r"E:\team project\uploads\uploads\binary_data_output.json"

# 加载数据
with open(json_file_path, 'r') as f:
    data = json.load(f)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 发送每条数据作为UDP包
for entry in data:
    packet = json.dumps(entry).encode('utf-8')  # 将JSON数据转换为字节
    sock.sendto(packet, (UDP_IP, UDP_PORT))     # 发送数据包
    time.sleep(1)  # 每秒发送一次数据包，模拟实时数据流
