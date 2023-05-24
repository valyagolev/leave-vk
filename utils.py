import datetime
import pytz

def timestamp_to_moscow_datetime(ts):
    local_tz = pytz.timezone('Europe/Moscow')
    dt = datetime.datetime.utcfromtimestamp(ts).replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(local_tz)