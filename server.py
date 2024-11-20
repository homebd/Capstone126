from flask import Flask, request, jsonify
import threading
import os
from PIL import Image
import io
import mediapipe as mp
import cv2
import numpy as np

app = Flask(__name__)

# Mediapipe 초기화
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False)

# 이미지 처리 함수
def process_image_and_return_json(image):
    # PIL 이미지를 OpenCV 이미지로 변환
    open_cv_image = np.array(image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()  # RGB로 변환

    # Mediapipe Pose 적용
    results = pose.process(open_cv_image)
    
    if not results.pose_landmarks:
        return {"error": "No pose landmarks detected"}
    
    # 포즈 랜드마크를 JSON 형식으로 변환
    landmarks = []
    for landmark in results.pose_landmarks.landmark:
        landmarks.append({
            'x': landmark.x,
            'y': landmark.y,
            'z': landmark.z,
            'visibility': landmark.visibility
        })
    
    return {"landmarks": landmarks}

# Flask API 엔드포인트
@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    try:
        # 이미지를 열고 처리
        image = Image.open(io.BytesIO(file.read()))
        result_json = process_image_and_return_json(image)
        return jsonify(result_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask 서버 실행
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# ngrok 실행
def run_ngrok():
    os.system("ngrok http 5000")

# Flask와 ngrok를 각각 다른 쓰레드로 실행
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

ngrok_thread = threading.Thread(target=run_ngrok)
ngrok_thread.daemon = True
ngrok_thread.start()
