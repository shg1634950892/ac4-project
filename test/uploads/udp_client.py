import socket

def send_udp_packet():
    # 创建 UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 要发送的数据，格式为 "IP|Name"
    message = "192.168.1.1|TestUser"

    # 发送数据到服务器
    sock.sendto(message.encode('utf-8'), ('127.0.0.1', 1206))

    print("Sent packet:", message)

if __name__ == "__main__":
    send_udp_packet()
