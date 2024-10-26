import socket

def bytes_to_hex(data):
    return ' '.join(f'{byte:02X}' for byte in data)

def interpret_data(raw_data):
    try:
        # 假设数据格式为 IP|Name
        data = raw_data.decode('utf-8').strip()
        parts = data.split('|')

        if len(parts) >= 2:
            ip_address = parts[0]
            name = parts[1]
            print(f"IP Address: {ip_address}")
            print(f"Name: {name}")
        else:
            print(f"Unexpected data format: {data}")

    except Exception as e:
        print(f"Error interpreting data: {e}")

def main():
    # 创建 UDP Socket 并监听端口 1206
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 1206))

    print("Listening for packets...")

    while True:
        try:
            # 接收数据包
            raw_data, addr = sock.recvfrom(4096)
            length = len(raw_data)
            print(f"Received packet with length: {length}")
            print(f"Raw data (hex): {bytes_to_hex(raw_data)}")

            # 解析数据
            interpret_data(raw_data)

        except Exception as e:
            print(f"Error receiving packet: {e}")

if __name__ == "__main__":
    main()
