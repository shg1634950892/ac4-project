import socket
import json

# 目标地址和端口
UDP_IP = "127.0.0.1"  # 如果是发送到本地主机，使用127.0.0.1
UDP_PORT = 1206  # 你配置的UDP监听端口

# 创建示例JSON数据
data = json.dumps({
    "Time": 123456789,
    "Position": {"x": 10.0, "y": 20.0, "z": 30.0},
    "Angles": {"x": 0.1, "y": 0.2, "z": 0.3},
    "Additional Data": {
        "Attribute 1": 1.0,
        "Attribute 2": 2.0,
        "Attribute 3": 3.0,
        "Attribute 4": 4.0,
        "Attribute 5": 5.0
    }
}).encode('utf-8')  # 编码为字节数据

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 发送UDP数据包
sock.sendto(data, (UDP_IP, UDP_PORT))

print(f"Sent data to {UDP_IP}:{UDP_PORT}")
