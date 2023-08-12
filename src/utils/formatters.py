import datetime
import sys

from pathlib import Path

src_path = Path(__file__.split("src")[0])
sys.path.append(src_path.as_posix())


def serialize_datetime(obj):
    if isinstance(obj, (datetime.datetime, datetime.date, int, type(None))):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, int):
            return str(obj)
        elif obj is None:
            return None
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
