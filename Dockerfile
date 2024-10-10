# Python 3.10 이미지 사용
FROM python:3.10-slim

# 작업 디렉터리 설정
WORKDIR /app

# 현재 디렉터리의 모든 파일을 Docker 이미지의 /app 디렉터리로 복사
COPY . /app

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 서버 실행
CMD ["python", "run.py"]
