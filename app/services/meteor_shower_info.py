# meteor_shower_info.py

from datetime import datetime
from app.data.data import METEOR_SHOWERS


def get_meteor_shower_info(comet_name, approach_time_str):
    """
    혜성과 관련된 유성우 정보를 반환하는 함수.
    """
    approach_date = datetime.strptime(approach_time_str, '%Y-%b-%d %H:%M').date()
    meteor_showers = METEOR_SHOWERS.get(comet_name, [])

    for shower in meteor_showers:
        start_month_day, end_month_day = shower['peak_period']
        start_month, start_day = map(int, start_month_day.split('-'))
        end_month, end_day = map(int, end_month_day.split('-'))

        # 유성우 기간 확인
        if (start_month, start_day) <= (approach_date.month, approach_date.day) <= (end_month, end_day):
            return {"name": shower["name"], "peak_period": shower["peak_period"]}

    return None