import os
import struct
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 创建上传文件夹（如果不存在）
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def parse_binary_data(binary_data):
    try:
        if len(binary_data) < 20:
            print("Insufficient data for parsing.")
            return None

        print(f"Raw binary data (hex): {binary_data.hex()}")

        # 使用小端格式解包数据
        latitude = struct.unpack('<f', binary_data[0:4])[0]
        longitude = struct.unpack('<f', binary_data[4:8])[0]
        speed = struct.unpack('<f', binary_data[8:12])[0]
        heading = struct.unpack('<f', binary_data[12:16])[0]
        time_stamp = struct.unpack('<I', binary_data[16:20])[0]

        print(f"Parsed values - Latitude: {latitude}, Longitude: {longitude}, Speed: {speed}, Heading: {heading}, Timestamp: {time_stamp}")

        # 验证经纬度和其他值
        if not (-90 <= latitude <= 90):
            print(f"Invalid latitude value: {latitude}")
            latitude = 0  # 使用默认值或其他处理方式
        if not (-180 <= longitude <= 180):
            print(f"Invalid longitude value: {longitude}")
            longitude = 0  # 使用默认值或其他处理方式
        if speed < 0 or speed > 50:  # 根据需要调整速度范围
            print(f"Invalid speed value: {speed}")
            speed = 0  # 使用默认值或其他处理方式
        if heading < 0 or heading >= 360:  # 航向的合理范围
            print(f"Invalid heading value: {heading}")
            heading = 0  # 使用默认值或其他处理方式

        return {
            "boat_position": {"latitude": latitude, "longitude": longitude},
            "speed": speed,
            "heading": heading,
            "time_stamp": time_stamp
        }

    except Exception as e:
        print(f"Error parsing binary data: {e}")
        return None




@app.route('/')
def upload_form():
    return render_template('test.html')

@socketio.on('upload_file')
def handle_file(data):
    try:
        # 解析上传的数据
        file_content = data['file']
        filename = data['filename']

        # 保存上传的文件为二进制
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(file_path, 'wb') as file:
            file.write(file_content.encode())

        parsed_data = []

        # 读取文件并解析每一段数据
        with open(file_path, 'rb') as f:
            while True:
                binary_data = f.read(20)
                if not binary_data:
                    break
                telemetry_data = parse_binary_data(binary_data)
                if telemetry_data:
                    parsed_data.append(telemetry_data)

        # 保存解析后的数据为 JSON
        json_filename = filename.rsplit('.', 1)[0] + '.json'
        json_file_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)

        with open(json_file_path, 'w') as json_file:
            json.dump(parsed_data, json_file, indent=4)

        # 返回解析的 JSON 数据
        socketio.emit('parsed_json', parsed_data)

    except Exception as e:
        socketio.emit('error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)










































