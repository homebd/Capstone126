from flask import Flask, request, jsonify
import threading
import os
import cv2
import numpy as np

app = Flask(__name__)

# Flask API 엔드포인트
@app.route('/process_frame', methods=['POST'])
def process_frame():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    try:
        # 이미지를 OpenCV 형식으로 변환
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # 이미지 처리 함수 (예: 낙상 감지)
        result_json = process_frame_to_json(frame, frame_count=0)
        if result_json:
            return jsonify(result_json)
        else:
            return jsonify({"error": "No landmarks detected"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask 서버 실행
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# ngrok 실행 및 URL 얻기
def run_ngrok():
    os.system("ngrok http 5000 &")
    time.sleep(5)  # ngrok가 시작할 시간을 주기 위해 잠시 대기
    response = os.popen('curl -s localhost:4040/api/tunnels | jq -r ".tunnels[0].public_url"').read().strip()
    print("ngrok URL:", response)
    return response

# URL을 라즈베리파이로 전송
def send_ngrok_url_to_raspberry_pi(ngrok_url, raspberry_pi_ip):
    raspberry_pi_endpoint = f"http://{raspberry_pi_ip}:5000/update_ngrok_url"
    response = requests.post(raspberry_pi_endpoint, json={"ngrok_url": ngrok_url})
    if response.status_code == 200:
        print("Successfully sent ngrok URL to Raspberry Pi")
    else:
        print("Failed to send ngrok URL:", response.status_code, response.text)

# Flask와 ngrok를 각각 다른 쓰레드로 실행
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

ngrok_thread = threading.Thread(target=run_ngrok)
ngrok_thread.daemon = True
ngrok_url = ngrok_thread.start()

# 라즈베리파이 IP 주소 (실제 주소로 변경 필요)
raspberry_pi_ip = "192.168.1.100"
send_ngrok_url_to_raspberry_pi(ngrok_url, raspberry_pi_ip)
