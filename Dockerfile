# Python 3.10 이미지 사용
FROM python:3.10-slim

# 작업 디렉터리 설정
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev-compat \
    libmariadb-dev \
    gcc \
    build-essential

# PYTHONPATH 환경 변수 설정
ENV PYTHONPATH "${PYTHONPATH}:/app"

# requirements.txt 파일만 복사
COPY requirements.txt /app/

# 필요한 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉터리의 모든 파일을 Docker 이미지의 /app 디렉터리로 복사
COPY . /app

# 서버 실행
CMD ["python", "run.py"]
