import datetime
import json


def dict_to_json(x: dict) -> str:
    return json.dumps(x, indent=4)

def time_to_str(t: datetime.datetime) -> str:
    return t.strftime("%Y-%m-%d %H:%M:%S")