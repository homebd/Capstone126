# 산학실전캡스톤1

### 주제: 모션 캡처를 활용한 환자 이상 징후(낙상) 분석 기술

### 협력처: KETI



## 팀소개

### 팀명: 팀126

### 팀원: 신해민, 기현빈, 송혜주, 김민재



## 사용 자원

### 카메라(Logitech C270, 720p 30fps)

### 임베디드 보드(Raspberry pi 5)

### GPU(Google colab pro, A100 GPU)



## 사용법

### 'server/'
- server.ipynb: 모델 파일 업로드 후 모든 셸 실행, 최하단 셸에 출력되는 URL 복사
- preprocessing.ipynb: 영상 파일 업로드 후 전처리 수행, keypoints를 json으로 반환
- upgrade_data.ipynb: keypoints json을 모델에 맞게 추가 전처리
- training.ipynb: 전처리된 데이터로 모델 학습
- best_model.keras: 학습이 완료된 모델 최종본


### 'client/'
- gui.py: 라즈베리파이 보드에서 실행하면 URL 입력창 표시, server.ipynb에서 복사한 URL 삽입하여 시작
