import socket
import struct
import threading
import json

# Local IP address and ports for receiving simulation software data
LOCAL_UDP_IP = "192.168.31.16"
LOCAL_UDP_PORT = 1206  # Port your simulation software is using for UDP
SIMULATOR_TCP_IP = "192.168.31.16"  # This should be your local IP or the IP of the simulator
SIMULATOR_TCP_PORT = 1207  # Port your simulation software is using for TCP

def decode_binary_data(binary_data):
    """Decode the binary data using the defined structure and convert it to JSON."""
    format_string = '<I I i i f f f f f f f i f ? f'
    
    try:
        # Unpack the binary data according to the format string
        size, message_type, simclock, sendtime, posx, posy, posz, anglex, angley, anglez, boomangle, tack, sailangletowind, luffing, finishtime = struct.unpack(format_string, binary_data[:struct.calcsize(format_string)])
        
        # Create a dictionary with the decoded values
        data_dict = {
            "Size": size,
            "Message Type": message_type,
            "Simclock": simclock,
            "Send Time": sendtime,
            "Position": {
                "X": posx,
                "Y": posy,
                "Z": posz
            },
            "Angle": {
                "X": anglex,
                "Y": angley,
                "Z": anglez
            },
            "Boom Angle": boomangle,
            "Tack": tack,
            "Sail Angle to Wind": sailangletowind,
            "Luffing": luffing,
            "Finish Time": finishtime
        }

        # Convert the dictionary to a JSON string
        json_data = json.dumps(data_dict, indent=4)
        
        # Print the JSON data
        print(json_data)

    except struct.error as e:
        print(f"Error decoding data: {e}")

def listen_for_tcp_data():
    """Function to listen for TCP data on the specified port and decode it in real-time."""
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((SIMULATOR_TCP_IP, SIMULATOR_TCP_PORT))  # Connect to the simulator's IP and TCP port

    print(f"Connected to TCP data on {SIMULATOR_TCP_IP}:{SIMULATOR_TCP_PORT}...")

    try:
        while True:
            data = tcp_socket.recv(4096)  # Adjust buffer size as needed
            if not data:
                print("Connection closed by the simulator.")
                break

            print(f"Received {len(data)} bytes from simulator (TCP)")

            # Decode the binary data from TCP packets
            decode_binary_data(data)

    except socket.error as e:
        print(f"Error receiving TCP data: {e}")
    finally:
        tcp_socket.close()

if __name__ == "__main__":
    # Start the TCP listening thread
    tcp_thread = threading.Thread(target=listen_for_tcp_data)

    # Start the thread
    tcp_thread.start()

    # Keep the main program running until the thread finishes
    tcp_thread.join()