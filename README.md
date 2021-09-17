# course-plus-data
## Folk from skyzh/course-plus-data.
## Reconfigured and Maintained By ToolmanP.
## My First Attempt to implement Docker
 Data for Course+.

## Usage
```
python -m course_plus_data_fetcher --output_file lessonData_2021-2022_1.json arrange 2021 1 10000
python sanitizer.py
```

Finally, modify `updated-at` in `lessonData_index.json`.
