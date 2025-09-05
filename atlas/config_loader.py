import json


def load_config(filepath: str) -> dict:
    with open(filepath, encoding='utf-8', mode='r') as f:
        config = json.load(f)

    return config
