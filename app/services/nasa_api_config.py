# nasa_api_config.py

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
NASA_API_KEY = os.getenv('NASA_API_KEY')
