import pytz


def local_to_utc(datetime):
    return datetime.astimezone(pytz.utc).replace(tzinfo=None)
