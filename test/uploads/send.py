import socket
import json

# 目标地址和端口
UDP_IP = "127.0.0.1"  # 如果是发送到本地主机，使用127.0.0.1
UDP_PORT = 1206  # 你配置的UDP监听端口

# JSON文件路径
file_path = 'binary_data_output.json'

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 打开并逐行读取JSON文件
with open(file_path, 'r') as file:
    for line in file:
        # 跳过空行
        if line.strip():
            try:
                # 尝试解析每行JSON数据
                json_data = json.loads(line)
                print(f"Sending JSON data: {json_data}")
                
                # 将JSON数据转换为字节并通过UDP发送
                data_bytes = json.dumps(json_data).encode('utf-8')
                sock.sendto(data_bytes, (UDP_IP, UDP_PORT))
                print(f"Sent data to {UDP_IP}:{UDP_PORT}")
                
            except json.JSONDecodeError as e:
                # 打印JSON解析错误
                print(f"Error decoding JSON: {e}")


