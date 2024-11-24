from flask import Flask, request, jsonify
import threading
import time
import requests
import cv2

app = Flask(__name__)

# 전역 변수로 ngrok URL 저장
ngrok_url = ""

@app.route('/update_ngrok_url', methods=['POST'])
def update_ngrok_url():
    global ngrok_url
    ngrok_url = request.json.get('ngrok_url', '')
    print("Received ngrok URL:", ngrok_url)
    shutdown_server()
    return jsonify({"status": "success"})

@app.route('/get_ngrok_url', methods=['GET'])
def get_ngrok_url():
    return jsonify({"ngrok_url": ngrok_url})

def run_flask():
    app.run(host='0.0.0.0', port=5000)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

# Flask 서버 실행 (백그라운드에서 실행)
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# ngrok URL을 가져오기 위해 서버 대기
def fetch_ngrok_url():
    global ngrok_url
    while not ngrok_url:  # ngrok URL을 받을 때까지 대기
        time.sleep(1)
    return ngrok_url

# Flask 서버 URL 자동 설정
flask_server_url = fetch_ngrok_url() + "/process_frame"

# 웹캠 초기화
camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to capture frame.")
        break

    # 프레임을 JPEG로 인코딩
    _, buffer = cv2.imencode('.jpg', frame)

    # Flask 서버로 전송
    try:
        response = requests.post(
            flask_server_url,
            files={"file": buffer.tobytes()}
        )
        if response.status_code == 200:
            print("Response from server:", response.json())
        else:
            print("Failed to process frame:", response.status_code, response.text)
    except Exception as e:
        print("Connection error:", e)

    # 키 입력으로 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
