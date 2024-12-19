import sys
import cv2
import requests
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QInputDialog, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon
import time
import threading

from gpiozero import TonalBuzzer, LED
from gpiozero.tones import Tone

led = LED(23)
buz = TonalBuzzer(18)

session = requests.Session()

thread_lock = threading.Lock()
frame_count = 0

class FallDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.colab_server_url = None
        self.prompt_server_url()

        self.initUI()

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.fall_detected = False


    def prompt_server_url(self):
        while True:
            input_dialog = QInputDialog(self)
            input_dialog.setWindowTitle("Colab Server URL")
            input_dialog.setLabelText("Enter the Colab Server URL:")
            input_dialog.resize(input_dialog.width() * 3, input_dialog.height())
            ok = input_dialog.exec_()
            text = input_dialog.textValue()

            if ok and text:
                if self.validate_url(f"{text}/process_frame"):
                    self.colab_server_url = f"{text}/process_frame"
                    break
                else:
                    QMessageBox.warning(self, "Invalid URL", "The URL you entered is invalid or the server is not running.\nPlease try again.")
            else:
                QMessageBox.critical(self, "No URL Provided", "You must provide a valid server URL to proceed.")
                sys.exit()

    def validate_url(self, url):
        try:
            response = requests.post(url, data={'test': 'test'})
            print(f"URL validation response: {response.status_code}")
            return response.status_code in [200, 400]
        except Exception as e:
            print(f"Error validating URL: {e}")
            return False

    def initUI(self):
        self.setWindowTitle("Fall Detection System")
        self.setGeometry(100, 100, 1280, 600)

        self.setWindowIcon(QIcon("/home/pi/logo.png"))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)


        title_layout = QHBoxLayout()
        real_label = QLabel("Real Images", self)
        real_label.setAlignment(Qt.AlignCenter)
        real_label.setStyleSheet("font-size: 30px; font-weight: bold;")
        title_layout.addWidget(real_label)

        model_label = QLabel("Model Application Images", self)
        model_label.setAlignment(Qt.AlignCenter)
        model_label.setStyleSheet("font-size: 30px; font-weight: bold;")
        title_layout.addWidget(model_label)
        main_layout.addLayout(title_layout)


        video_layout = QHBoxLayout()
        self.input_video_label = QLabel(self)
        self.input_video_label.setFixedSize(640, 480)
        self.input_video_label.setStyleSheet("background-color: black; border: 1px solid gray;")
        video_layout.addWidget(self.input_video_label)

        self.output_video_label = QLabel(self)
        self.output_video_label.setFixedSize(640, 480)
        self.output_video_label.setStyleSheet("background-color: black; border: 1px solid gray;")
        video_layout.addWidget(self.output_video_label)
        main_layout.addLayout(video_layout)


        button_layout = QHBoxLayout()

        start_button = QPushButton("START", self)
        start_button.setFixedSize(100, 40)
        start_button.clicked.connect(self.start_detection)
        button_layout.addWidget(start_button)

        exit_button = QPushButton("EXIT", self)
        exit_button.setFixedSize(100, 40)
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)

        button_layout.setAlignment(Qt.AlignRight)
        main_layout.addLayout(button_layout)

    def start_detection(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Could not access the camera.")
            return

        #self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        #self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.timer.start(50)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        
        
        self.frm_rs_thread = threading.Thread(target=self.frame_skip, args=(frame, ))
        self.frm_rs_thread.start()
        
    
    def frame_skip(self, frame):
        global frame_count
        
        frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
        processed_frame = self.send_frame_to_colab(frame)
        
        with thread_lock:
            if frame_count % 2 == 0:
                self.output_thread = threading.Thread(target=self.update_output_frame, args=(processed_frame,))
                self.output_thread.start()
                self.input_thread = threading.Thread(target=self.update_input_frame, args=(frame,))
                self.input_thread.start()
            frame_count += 1


        
    def update_input_frame(self, frame):
        
        
        self.display_frame(frame, self.input_video_label)
            
    def update_output_frame(self, frame):
        processed_frame = frame
        
        
        
        if processed_frame is not None:
            self.display_frame(processed_frame, self.output_video_label)
        else:
            print("Processed frame is None. Check Colab server response.")

    def send_frame_to_colab(self, frame):
        if not self.colab_server_url:
            print("Colab server URL not set.")
            return None
            

        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'file': img_encoded.tobytes()}

        try:
            response = session.post(self.colab_server_url, files=files, stream=True)

            if response.status_code == 200:
                np_bytes = np.frombuffer(response.content, np.uint8)
                processed_frame = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
                with thread_lock:
                    if self.fall_detected:
                        self.fall_detected = False
                return processed_frame
            elif response.status_code == 201:
                np_bytes = np.frombuffer(response.content, np.uint8)
                processed_frame = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
                with thread_lock:
                    if not self.fall_detected:
                        self.fall_detected = True
                        QTimer.singleShot(0, self.show_falling_alert)
                        self.activate_buzzer_and_led()
                return processed_frame
            else:
                return None
        except Exception as e:
            print(f"Error communicating with Colab: {e}")
            return None

    def activate_buzzer_and_led(self):
        threading.Thread(target=self.led_blinking_loop, daemon=True).start()
        threading.Thread(target=self.buzzer_pattern, daemon=True).start()

    def led_blinking_loop(self):
        while self.fall_detected:
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(0.5)

    def buzzer_pattern(self):
        while self.fall_detected:
            buz.play(Tone('G5'))
            time.sleep(1)
            buz.stop()
            time.sleep(0.5)

    def show_falling_alert(self):
        alert_dialog = CustomAlertDialog(self)
        alert_dialog.exec_()

    def display_frame(self, frame, label):
        if frame is None:
            print("Error: Frame is None in display_frame.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qimg))
        #label.setScaledContents(True)

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        led.off()
        buz.stop()
        event.accept()

class CustomAlertDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fall Detected!")
        self.setFixedSize(800, 300)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)

        img_label = QLabel(self)
        pixmap = QPixmap("/home/pi/FallDetection.png")
        img_label.setPixmap(pixmap.scaled(600, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(img_label)

        text_label = QLabel("Click the screen or press any key", self)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("color: gray; font-size: 18px; font-weight: bold; background: transparent;")
        layout.addWidget(text_label)

        self.center_on_parent()

    def center_on_parent(self):
        parent_geometry = self.parent().geometry()
        parent_x = parent_geometry.x()
        parent_y = parent_geometry.y()
        parent_width = parent_geometry.width()
        parent_height = parent_geometry.height()

        dialog_width = self.width()
        dialog_height = self.height()

        center_x = parent_x + (parent_width - dialog_width) // 2
        center_y = parent_y + (parent_height - dialog_height) // 2

        self.move(center_x, center_y)

    def mousePressEvent(self, event):
        self.close()

    def keyPressEvent(self, event):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FallDetectionApp()
    window.show()
    sys.exit(app.exec_())

