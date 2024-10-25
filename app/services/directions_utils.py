# directions_utils.py

def azimuth_to_direction(azimuth):
    """
    방위각을 동서남북 방향으로 변환하는 함수

    Args:
        azimuth (float): 방위각 (0 ~ 360도).

    Returns:
        str: 방위 방향 ("North", "Northeast", "East", "Southeast", "South", "Southwest", "West", "Northwest").
    """
    if 0 <= azimuth < 22.5 or 337.5 <= azimuth <= 360:
        return "North"
    elif 22.5 <= azimuth < 67.5:
        return "Northeast"
    elif 67.5 <= azimuth < 112.5:
        return "East"
    elif 112.5 <= azimuth < 157.5:
        return "Southeast"
    elif 157.5 <= azimuth < 202.5:
        return "South"
    elif 202.5 <= azimuth < 247.5:
        return "Southwest"
    elif 247.5 <= azimuth < 292.5:
        return "West"
    elif 292.5 <= azimuth < 337.5:
        return "Northwest"
    else:
        return "Unknown"
