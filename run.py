# 실행
import faulthandler
import logging
from flask_cors import CORS  # Flask-CORS import 추가
from app import create_app

# print("Google Time Zone API Key:", os.getenv('GOOGLE_TIMEZONE_API_KEY'))

faulthandler.enable()  # 메모리 검사 도구

# 디버깅 로거 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Flask 애플리케이션 생성
    try:
        app = create_app()
        # CORS(app, resources={r"/*": {"origins": "*"}})  # CORS 활성화
        logger.debug("Flask application created successfully")
    except Exception as e:
        logger.critical(f"Failed to create Flask application: {e}", exc_info=True)
        raise

    # 애플리케이션 실행
    try:
        logger.info("Starting Flask application")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.critical(f"Failed to run Flask application: {e}", exc_info=True)
        raise
