import os
import json
from flask import jsonify

def setup_api_routes(app):
    @app.route('/api/get_sailing_data', methods=['GET'])
    def get_sailing_data():
        try:
            file_path = os.path.join(os.getcwd(), 'binary_data_output.json')
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        parsed_line = json.loads(line)
                        data.append(parsed_line)
                    except json.JSONDecodeError:
                        print(f"Error decoding line: {line}")  # 输出出错的行
            return jsonify(data)
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400


