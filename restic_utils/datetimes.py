import datetime

import dateutil.parser
import pytz


def parse_iso_8601_to_naive_utc_datetime(datetime_str: str) -> datetime.datetime:
    return pytz.utc.normalize(dateutil.parser.parse(datetime_str)).replace(tzinfo=None)


def naive_utc_now() -> datetime.datetime:
    return datetime.datetime.utcnow()
