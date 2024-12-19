# 산학실전캡스톤1

- 주제: 모션 캡처를 활용한 환자 이상 징후(낙상) 분석 기술

- 협력처: KETI



## 팀소개

- 팀명: 팀126

- 팀원: 신해민, 기현빈, 송혜주, 김민재


## 프로젝트 설명

### 개요

- 고령 사회에 진입에 따라 낙상 감지 기술 필요성 대두
- 기존 웨어러블 디바이스 및 센서 기반 시스템의 경우 불편함과 정확도 이슈

### 프로젝트 설계

1. 모션 캡처를 활용한 환자 이상 징후(낙상) 분석 기술
i) 모션 캡처: mediapipe
ii) 이상 징후 분석: 모델 학습

3. 클라이언트와 서버 분류하여 작업(일체화 시: 보드의 가격 상승, 경제성 저하)
i) 클라이언트: 라즈베리파이 보드
ii) 서버: 구글 코랩 클라우드 서버

### 프로젝트 구조

1. 라즈베리파이에서 웹캠을 통해 영상 촬영
2. 클라우드 서버로 영상을 캡처해 이미지 전송
3. mediapipe를 통해 이미지 분석
4. 분석된 결과와 사전 학습한 모델을 통해 포즈 분석
5. 결과를 라즈베리파이로 전송, 낙상 시 구글 드라이브에 낙상 영상 저장
6. 라즈베리파이에서 GUI에 결과 및 LED, 부저 신호 출력

## 사용 자원

- 카메라(Logitech C270, 720p 30fps)
- 임베디드 보드(Raspberry pi 5)
- GPU(Google colab pro, A100 GPU)



## 사용법

### 'server/'
- server.ipynb: 모델 파일 업로드 후 모든 셸 실행, 최하단 셸에 출력되는 URL 복사
- preprocessing.ipynb: 영상 파일 업로드 후 전처리 수행, keypoints를 json으로 반환
- upgrade_data.ipynb: keypoints json을 모델에 맞게 추가 전처리
- training.ipynb: 전처리된 데이터로 모델 학습
- best_model.keras: 학습이 완료된 모델 최종본


### 'client/'
- gui.py: 라즈베리파이 보드에서 실행하면 URL 입력창 표시, server.ipynb에서 복사한 URL 삽입하여 시작
