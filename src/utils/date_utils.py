from datetime import datetime, time, timedelta

def adjust_to_nearest_10_minute_interval(ts):
    dt = datetime.fromtimestamp(ts)
    dt = dt.replace(minute=(dt.minute // 10) * 10, second=0, microsecond=0)
    return int(dt.timestamp())

def get_adjusted_timestamp(date: datetime) -> int:
    date_timestamp = int(date.timestamp())
    return adjust_to_nearest_10_minute_interval(date_timestamp)

def get_today_date_range() -> tuple[datetime, datetime]:
    now = datetime.now()
    from_date = datetime.combine(now.date(), time.min)
    to_date = datetime.combine(now.date(), time.max)
    return from_date, to_date

def get_month_date_range() -> tuple[datetime, datetime]:
    now = datetime.now()
    from_date = datetime(now.year, now.month, 1)
    to_date = from_date + timedelta(days=30)
    return from_date, to_date