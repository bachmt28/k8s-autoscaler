# autoscaler/time_rule_utils.py

from datetime import datetime


def parse_days(days_str):
    # Chuyển Mon-Fri thành list ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    day_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    parts = days_str.split(",")
    result = []

    for part in parts:
        if "-" in part:
            start, end = part.split("-")
            i = day_map.index(start.strip())
            j = day_map.index(end.strip())
            if i <= j:
                result.extend(day_map[i:j + 1])
            else:  # vòng qua tuần
                result.extend(day_map[i:] + day_map[:j + 1])
        else:
            result.append(part.strip())
    return result


def parse_hours(hours_str):
    # Chuyển 08h-18h thành (8, 18)
    try:
        start_str, end_str = hours_str.replace("h", "").split("-")
        return int(start_str), int(end_str)
    except Exception:
        return 0, 23  # fallback toàn thời gian


def is_time_in_range(rule, now: datetime):
    now_day = now.strftime("%a")  # VD: 'Mon'
    now_hour = now.hour

    days = parse_days(rule.days)
    start_hour, end_hour = parse_hours(rule.hours)

    if now_day not in days:
        return False

    return start_hour <= now_hour < end_hour
