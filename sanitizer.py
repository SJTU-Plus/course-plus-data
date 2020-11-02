import json
import re

from os import walk
from pathlib import Path


def process_json(filename):
    obj = json.loads(Path(filename).read_text(encoding="utf-8"))
    cnt = {}
    for key in range(len(obj)):
        for data_key in obj[key].keys():
            if data_key == 'xkbz' and isinstance(obj[key][data_key], str):
                raw_content = obj[key][data_key]
                obj[key][data_key] = re.sub(r'([0-9]{7,})', 'XXXXXXXX', raw_content)
                if obj[key][data_key] != raw_content:
                    cnt[data_key] = cnt.get(data_key, 0) + 1
    print(cnt)
    Path(filename).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


for (dirpath, dirnames, filenames) in walk("."):
    for filename in filenames:
        if filename.endswith(".json") and filename.startswith("lessonData"):
            process_json(filename)
    break
