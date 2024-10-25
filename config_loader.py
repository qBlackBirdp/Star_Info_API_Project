# # config_loader.py
# # DB 설정.
#
# import yaml
# import os
# import logging
#
# # 로깅 설정
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#
#
# def load_db_config():
#     try:
#         config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
#         logging.info(f"Config path: {config_path}")
#
#         with open(config_path, 'r') as file:
#             config = yaml.safe_load(file)
#
#         db_config = {
#             'user': config['database']['user'],
#             'password': config['database']['password'],
#             'host': config['database']['host'],
#             'port': int(config['database']['port']),  # 포트는 정수로 변환
#             'database': config['database']['database']
#         }
#
#         logging.info(
#             f"Database config loaded successfully: {db_config['host']}:{db_config['port']}/{db_config['database']}")
#
#         return db_config
#
#     except FileNotFoundError:
#         logging.error("config.yml 파일을 찾을 수 없습니다. 경로를 확인하세요.")
#     except KeyError as e:
#         logging.error(f"config.yml 파일에 누락된 키가 있습니다: {e}")
#     except Exception as e:
#         logging.error(f"DB 설정을 불러오는 도중 예외가 발생했습니다: {e}")
