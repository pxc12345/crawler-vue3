from datetime import datetime, timedelta


LUNAR_FESTIVALS = {
    "春节": (1, 1),
    "中秋节": (8, 15),
}

LUNAR_TO_SOLAR = {
    2025: {
        (1, 1): (1, 29),
        (8, 15): (10, 6),
    },
    2026: {
        (1, 1): (2, 17),
        (8, 15): (9, 25),
    },
    2027: {
        (1, 1): (2, 6),
        (8, 15): (10, 4),
    },
    2028: {
        (1, 1): (1, 26),
        (8, 15): (9, 21),
    },
    2029: {
        (1, 1): (2, 13),
        (8, 15): (9, 10),
    },
    2030: {
        (1, 1): (2, 3),
        (8, 15): (9, 30),
    },
}


def _get_mothers_day(year):
    """计算母亲节：每年5月第二个星期日"""
    may_first = datetime(year, 5, 1)
    days_until_sunday = (6 - may_first.weekday()) % 7
    second_sunday = may_first + timedelta(days=days_until_sunday + 7)
    return second_sunday.day


def _get_solar_date(year, month, day, is_lunar):
    """将农历日期转换为公历日期"""
    if not is_lunar:
        return year, month, day

    key = (month, day)
    if year in LUNAR_TO_SOLAR and key in LUNAR_TO_SOLAR[year]:
        solar_month, solar_day = LUNAR_TO_SOLAR[year][key]
        return year, solar_month, solar_day

    return year, month, day


def calculate_nearest_festival(festivals):
    """计算当前时间之后最近的未过节日"""
    now = datetime.now()
    today = now.date()

    candidates = []

    for festival in festivals:
        name = festival["festival_name"]
        month = festival["month"]
        day = festival["day"]
        is_lunar = festival["is_lunar"]

        if name == "母亲节":
            day = _get_mothers_day(now.year)

        solar_year, solar_month, solar_day = _get_solar_date(now.year, month, day, is_lunar)

        try:
            festival_date = datetime(solar_year, solar_month, solar_day).date()
        except ValueError:
            festival_date = datetime(solar_year, solar_month, 1).date()

        candidates.append((name, festival_date))

        if name == "母亲节":
            next_day = _get_mothers_day(now.year + 1)
            next_solar = _get_solar_date(now.year + 1, month, next_day, is_lunar)
            candidates.append((name, datetime(next_solar[0], next_solar[1], next_solar[2]).date()))
            continue

        next_solar = _get_solar_date(now.year + 1, month, day, is_lunar)
        try:
            candidates.append((name, datetime(next_solar[0], next_solar[1], next_solar[2]).date()))
        except ValueError:
            candidates.append((name, datetime(next_solar[0], next_solar[1], 1).date()))

    nearest = None
    nearest_date = None

    for name, fdate in candidates:
        if fdate >= today:
            if nearest_date is None or fdate < nearest_date:
                nearest = name
                nearest_date = fdate

    if nearest is None:
        min_date = min(candidates, key=lambda x: x[1])
        nearest = min_date[0]

    return nearest


def generate_festival_text(festival_name):
    """根据节日名称生成默认祝福文案"""
    texts = {
        "元旦": "新的一年，新的开始。愿你拥抱每一个美好的瞬间，元旦快乐！",
        "春节": "新春佳节，万象更新。愿你和家人团团圆圆，幸福安康，春节快乐！",
        "情人节": "爱是世间最美好的语言。愿你的每一天都充满甜蜜与温暖，情人节快乐！",
        "母亲节": "妈妈的爱是世界上最无私的爱。愿天下所有的母亲健康快乐，母亲节快乐！",
        "中秋节": "月圆人团圆，千里共婵娟。愿你中秋快乐，阖家幸福！",
        "圣诞节": "愿圣诞的钟声为你带来平安与喜乐，祝你圣诞快乐，新年幸福！",
    }
    return texts.get(festival_name, f"祝你{festival_name}快乐，阖家幸福，万事如意！")