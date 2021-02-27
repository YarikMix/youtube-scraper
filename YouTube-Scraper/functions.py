import re

import json


def write_json(file_name, data):
    with open(f"{file_name}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

hours_pattern = re.compile(r"(\d+)H")
minutes_pattern = re.compile(r"(\d+)M")
seconds_pattern = re.compile(r"(\d+)S")

def get_video_duration(s):
    hours = hours_pattern.search(s)
    minutes = minutes_pattern.search(s)
    seconds = seconds_pattern.search(s)

    hours = int(hours.group(1)) if hours else 0
    minutes = int(minutes.group(1)) if minutes else 0
    seconds = int(seconds.group(1)) if seconds else 0

    return f"{hours}:{minutes}:{seconds}"


def get_video_release_date(s):
    year = s.split("-")[0]
    month = s.split("-")[1]
    day = s.split("-")[2][:2].replace("0", "")
    return f"{day}.{month}.{year}"


def get_last_value(dict):
    last_key = list(dict)[-1]
    last_value = dict[last_key]
    return last_value