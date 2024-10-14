# meteor_shower_service.py

import logging
from flask import Blueprint, jsonify
from gmn_python_api import data_directory as dd
from gmn_python_api import meteor_trajectory_reader

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)


def get_meteor_shower_forecast():
    """
    GMN API를 사용하여 유성우 예보 데이터를 가져오는 함수

    Returns:
        dict: 유성우 예보 정보
    """
    try:
        # GMN 데이터 디렉토리에서 특정 날짜의 데이터 가져오기 (예: 2024년 10월 13일)
        traj_file_content = dd.get_daily_file_content_by_date("2024-10-13")

        # 데이터를 Pandas DataFrame으로 읽기
        traj_df = meteor_trajectory_reader.read_data(traj_file_content)

        # 결측값을 빈 문자열로 대체
        traj_df = traj_df.fillna("")

        # 유성우 데이터를 반환
        meteor_shower_data = traj_df.to_dict(orient='records')
        logging.debug(f"Meteor Shower Data: {meteor_shower_data}")

        return meteor_shower_data
    except Exception as e:
        logging.error(f"Failed to fetch meteor shower data: {str(e)}")
        return {"error": "Failed to fetch meteor shower data"}


__all__ = ['get_meteor_shower_forecast']
