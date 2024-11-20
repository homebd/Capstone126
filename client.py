import cv2
import requests

# Flask 서버 URL (ngrok에서 제공된 URL로 변경 필요)
flask_server_url = "http://<your-ngrok-url>/process_frame"

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




'''
import cv2
import requests
import threading

# ngrok 퍼블릭 URL
COLAB_SERVER_URL = 'https://50ed-34-126-65-19.ngrok-free.app/process'

# 카메라 초기화
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 전송할 이미지를 저장할 큐
image_queue = []

def capture_images():
    for i in range(40):  # 10초 동안 1초에 4장씩 촬영
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        # 큐에 이미지 추가
        image_queue.append(frame)
        time.sleep(0.25)  # 0.25초마다 촬영

    cap.release()

def send_images():
    while True:
        if image_queue:
            frame = image_queue.pop(0)

            # 이미지 인코딩
            _, img_encoded = cv2.imencode('.jpg', frame)

            # 서버로 POST 요청 보내기 (멀티파트 데이터로 전송)
            files = {'file': ('fixed_image.jpg', img_encoded.tobytes(), 'image/jpeg')}
            response = requests.post(COLAB_SERVER_URL, files=files)

            # 응답 상태 코드 및 결과 출력
            print(response.status_code)
            if response.status_code == 200:
                print(response.json())  # 서버의 JSON 응답 출력
            else:
                print("Error:", response.text)

# 이미지 캡처 스레드 시작
capture_thread = threading.Thread(target=capture_images)
capture_thread.start()

# 이미지 전송 스레드 시작
send_thread = threading.Thread(target=send_images)
send_thread.start()
'''
