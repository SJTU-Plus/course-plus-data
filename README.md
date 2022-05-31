# course-plus-data

Data for Course+.

## Usage

```
export SJTU_USER=xxx
export SJTU_PASS=xxx
pipenv run python -m course_plus_data_fetcher --output_file lessonData_2022-2023_1.json arrange 2022 1 10000
pipenv run python -m course_plus_data_fetcher --output_file lesson_conversion.json conversion 10000
pipenv run python -m course_plus_data_fetcher --output_file lesson_description_2022.json description 2022
pipenv run python sanitizer.py
```

dsd

Finally, modify `updated-at` in `lessonData_index.json`.
