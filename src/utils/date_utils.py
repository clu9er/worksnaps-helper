from datetime import datetime

def adjust_to_nearest_10_minute_interval(ts):
    dt = datetime.fromtimestamp(ts)
    dt = dt.replace(minute=(dt.minute // 10) * 10, second=0, microsecond=0)
    return int(dt.timestamp())

def get_adjusted_timestamp(date: datetime) -> int:
    date_timestamp = int(date.timestamp())
    return adjust_to_nearest_10_minute_interval(date_timestamp)