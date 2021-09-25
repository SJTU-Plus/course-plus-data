# course-plus-data
## Folk from skyzh/course-plus-data.
## Reconfigured and Maintained By ToolmanP.
## My First Attempt to implement Docker
 Data for Course+.

## For python
```
python -m course_plus_data_fetcher
```
## For docker
```
docker build -t *your docker tag*  .
docker run -v */dir/json_directory* :/app/json -e SJTU_USER=xxxxxxxxx -e  SJTU_USER=xxxxxxx *your docker tag*

```