import json

from os import walk
from pathlib import Path

def process_json(filename):
    obj = json.loads(Path(filename).read_text(), encoding="utf-8")
    cnt = {}
    for key in range(len(obj)):
        for data_key in obj[key].keys():
            if isinstance(obj[key][data_key], str) and "zoom" in obj[key][data_key].lower():
                obj[key][data_key] = "<ZOOM info masked>"
                cnt[data_key] = cnt.get(data_key, 0) + 1
    print(cnt)
    Path(filename).write_text(json.dumps(obj, ensure_ascii=False, indent=True), encoding="utf-8")

for (dirpath, dirnames, filenames) in walk("."):
    for filename in filenames:
        if filename.endswith(".json") and filename.startswith("lessonData"):
            process_json(filename)
    break
