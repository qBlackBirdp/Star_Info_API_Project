# meteor_shower_info.py

from datetime import datetime
from app.data.data import METEOR_SHOWERS


def get_meteor_shower_info(comet_name, approach_time_str):
    """
    혜성과 관련된 유성우 정보를 반환하는 함수.
    """
    approach_date = datetime.strptime(approach_time_str, '%Y-%b-%d %H:%M').date()
    meteor_showers = METEOR_SHOWERS.get(comet_name, [])

    shower_info_list = []

    for shower in meteor_showers:
        start_month_day, end_month_day = shower['peak_period']
        start_month, start_day = map(int, start_month_day.split('-'))
        end_month, end_day = map(int, end_month_day.split('-'))

        # 유성우 극대기 기간 확인
        peak_start_date = datetime(approach_date.year, start_month, start_day).date()
        peak_end_date = datetime(approach_date.year, end_month, end_day).date()

        if peak_start_date <= approach_date <= peak_end_date:
            shower_info_list.append({
                "name": shower["name"],
                "peak_period": shower["peak_period"],
                "message": "Meteor shower is at its peak period."
            })
        else:
            shower_info_list.append({
                "name": shower["name"],
                "peak_period": shower["peak_period"],
                "message": "Meteor shower is not at its peak period."
            })

    return shower_info_list if shower_info_list else None


def get_general_meteor_shower_info(comet_name):
    """
    혜성과 관련된 유성우 정보를 반환하는 함수.
    """
    meteor_showers = METEOR_SHOWERS.get(comet_name, [])
    return [{"name": shower["name"], "peak_period": shower["peak_period"]} for shower in meteor_showers]
