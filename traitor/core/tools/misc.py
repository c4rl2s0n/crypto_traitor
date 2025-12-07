import json


def dict_to_json(x: dict) -> str:
    return json.dumps(x, indent=4)
