# # app/routes/db_test_routes.py
#
# from flask_restx import Namespace, Api, Resource
# from flask import Blueprint, request
# from app.db.db_utils import get_session
# import random
# import string
# from datetime import datetime
# from sqlalchemy.sql import text
#
# # Blueprint와 Namespace 등록
# db_test_blueprint = Blueprint('db_test', __name__, url_prefix='/api/db_test')
# db_test_api = Api(db_test_blueprint, doc='/doc')  # Swagger UI 경로 설정
# db_test_ns = Namespace('db_test', description="Database Test Operations")
#
# db_test_api.add_namespace(db_test_ns)
#
# TABLE_NAME = "test_data"
#
#
# def ensure_table_exists(session, db_type):
#     """
#     테이블이 없으면 생성하는 함수 (DB 연결 확인 포함)
#     """
#     try:
#         session.execute(text("SELECT 1"))
#     except Exception as e:
#         raise RuntimeError(f"Database connection failed: {str(e)}")
#
#     if db_type == "mariadb":
#         create_table_query = text(f"""
#         CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             name VARCHAR(255),
#             value INT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         """)
#     elif db_type == "postgres":
#         create_table_query = text(f"""
#         CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(255),
#             value INT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         """)
#     else:
#         raise ValueError(f"Unsupported database type: {db_type}")
#
#     session.execute(create_table_query)
#     session.commit()
#
#
# def drop_table(session, db_type):
#     """
#     테이블 삭제 함수
#     """
#     drop_table_query = text(f"DROP TABLE IF EXISTS {TABLE_NAME};")
#     session.execute(drop_table_query)
#     session.commit()
#
#
# # INSERT 엔드포인트
# @db_test_ns.route('/insert/<string:db_type>')
# class InsertData(Resource):
#     def post(self, db_type):
#         """
#         데이터 삽입 엔드포인트
#         """
#         data = request.json
#         num_rows = data.get("rows", 1000)
#
#         with get_session(db_type) as session:
#             ensure_table_exists(session, db_type)
#
#             data_to_insert = [
#                 {
#                     "name": ''.join(random.choices(string.ascii_letters, k=10)),
#                     "value": random.randint(1, 1000),
#                     "created_at": datetime.utcnow()
#                 }
#                 for _ in range(num_rows)
#             ]
#             session.execute(text(f"""
#                 INSERT INTO {TABLE_NAME} (name, value, created_at)
#                 VALUES (:name, :value, :created_at)
#             """), data_to_insert)
#             session.commit()
#
#         return {"message": f"{num_rows} rows inserted into {db_type}."}, 200
#
#
# # QUERY 엔드포인트
# @db_test_ns.route('/query/<string:db_type>')
# class QueryData(Resource):
#     def get(self, db_type):
#         """
#         데이터 조회 엔드포인트
#         """
#         with get_session(db_type) as session:
#             ensure_table_exists(session, db_type)
#
#             result = session.execute(text(f"SELECT * FROM {TABLE_NAME};")).fetchall()
#
#             def serialize_row(row):
#                 row_dict = dict(row._mapping)
#                 for key, value in row_dict.items():
#                     if isinstance(value, datetime):
#                         row_dict[key] = value.isoformat()
#                 return row_dict
#
#             data = [serialize_row(row) for row in result]
#
#         return {"rows": len(data), "data": data}, 200
#
#
# # UPDATE 엔드포인트
# @db_test_ns.route('/update/<string:db_type>')
# class UpdateData(Resource):
#     def post(self, db_type):
#         """
#         데이터 수정 엔드포인트
#         """
#         data = request.json
#         target_value = data.get("value", 500)
#         new_value = data.get("new_value", 999)
#
#         with get_session(db_type) as session:
#             ensure_table_exists(session, db_type)
#
#             session.execute(text(f"""
#                 UPDATE {TABLE_NAME}
#                 SET value = :new_value
#                 WHERE value > :target_value
#             """), {"new_value": new_value, "target_value": target_value})
#             session.commit()
#
#         return {"message": f"Rows with value > {target_value} updated in {db_type}."}, 200
#
#
# # DELETE 엔드포인트
# @db_test_ns.route('/delete/<string:db_type>')
# class DeleteData(Resource):
#     def post(self, db_type):
#         """
#         데이터 삭제 엔드포인트
#         """
#         data = request.json
#         target_value = data.get("value", None)
#         created_after = data.get("created_after", None)
#
#         with get_session(db_type) as session:
#             ensure_table_exists(session, db_type)
#
#             if target_value:
#                 session.execute(text(f"DELETE FROM {TABLE_NAME} WHERE value > :target_value"),
#                                 {"target_value": target_value})
#             elif created_after:
#                 session.execute(text(f"DELETE FROM {TABLE_NAME} WHERE created_at >= :created_after"),
#                                 {"created_after": created_after})
#             else:
#                 session.execute(text(f"DELETE FROM {TABLE_NAME}"))
#
#             session.commit()
#
#         return {"message": "Rows deleted in {db_type}."}, 200
#
#
# # DROP 엔드포인트
# @db_test_ns.route('/drop/<string:db_type>')
# class DropTable(Resource):
#     def post(self, db_type):
#         """
#         테이블 삭제 엔드포인트
#         """
#         with get_session(db_type) as session:
#             drop_table(session, db_type)
#
#         return {"message": f"Table {TABLE_NAME} dropped in {db_type}."}, 200
