import datetime
import pytz
import os

def timestamp_to_moscow_datetime(ts):
    local_tz = pytz.timezone('Europe/Moscow')
    dt = datetime.datetime.utcfromtimestamp(ts).replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(local_tz)

def create_dir(dir):
    try:
        os.makedirs(dir)
    except FileExistsError:
        # print('directory %s already exists, skipping' % dir)
        pass