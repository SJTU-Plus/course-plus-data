# course-plus-data
# folk from skyzh/course-plus-data
# reconfigure by ToolmanP
Data for Course+.

## Usage

```
export SJTU_USER=xxx
export SJTU_PASS=xxx
pipenv run python -m course_plus_data_fetcher --output_file lessonData_2021-2022_1.json arrange 2021 1 10000
pipenv run python sanitizer.py
```

Finally, modify `updated-at` in `lessonData_index.json`.
