# 실행
import multiprocessing as mp
import logging
from app import create_app
import faulthandler
import os
print("Google Time Zone API Key:", os.getenv('GOOGLE_TIMEZONE_API_KEY'))


faulthandler.enable()  # 메모리 검사 도구

# 디버깅 로거 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # 프로세스 시작 방식을 'fork'으로 설정
    try:
        mp.set_start_method('fork')
        logger.debug("Multiprocessing start method set to 'fork'")
    except RuntimeError as e:
        logger.error(f"Failed to set start method: {e}")

    # Flask 애플리케이션 생성
    try:
        app = create_app()
        logger.debug("Flask application created successfully")
    except Exception as e:
        logger.critical(f"Failed to create Flask application: {e}", exc_info=True)
        raise

    # 애플리케이션 실행
    try:
        logger.info("Starting Flask application")
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.critical(f"Failed to run Flask application: {e}", exc_info=True)
        raise
# 실행
# import multiprocessing as mp
# import logging
# from app import create_app
# import faulthandler
# import os
#
# print("Google Time Zone API Key:", os.getenv('GOOGLE_TIMEZONE_API_KEY'))
#
# faulthandler.enable()  # 메모리 검사 도구
#
# # 디버깅 로거 설정
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
# logger = logging.getLogger(__name__)
#
# # Flask 애플리케이션 생성
# app = create_app()  # Gunicorn에서 사용할 수 있도록 전역으로 설정
# logger.debug("Flask application created successfully")
#
# if __name__ == '__main__':
#     # 프로세스 시작 방식을 'fork'으로 설정
#     try:
#         mp.set_start_method('fork')
#         logger.debug("Multiprocessing start method set to 'fork'")
#     except RuntimeError as e:
#         logger.error(f"Failed to set start method: {e}")
#
#     # 애플리케이션 실행
#     try:
#         logger.info("Starting Flask application")
#         app.run(host='0.0.0.0', port=5000)
#     except Exception as e:
#         logger.critical(f"Failed to run Flask application: {e}", exc_info=True)
#         raise
