# course-plus-data

Data for Course+.

## Usage

```
export SJTU_USER=xxx
export SJTU_PASS=xxx
pipenv run python -m course_plus_data_fetcher --output_file lessonData_2023-2024_1.json arrange 2023 1 10000
pipenv run python -m course_plus_data_fetcher --output_file lesson_conversion.json conversion 10000
pipenv run python -m course_plus_data_fetcher --output_file lesson_description_2020.json description lessonData_2023-2024_1.json
pipenv run python sanitizer.py
```

dsd

Finally, modify `updated-at` in `lessonData_index.json`.
