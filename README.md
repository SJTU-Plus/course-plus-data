# course-plus-data

Folked from skyzh/course-plus-data.
 Data for Course+.

## For python
```
export SJTU_USER = xxxxxxxxx
export SJTU_PASS = xxxxxxxxx
python -m course_plus_data_fetcher
```
## For docker configuration
```
docker build -t *your docker tag*  .
docker run -v */dir/json_directory* :/app/json -e SJTU_USER=xxxxxxxxx -e  SJTU_USER=xxxxxxx *your docker tag*
```
or just run
```
docker run -v */dir/json_directory* :/app/json -e SJTU_USER=xxxxxxxxx -e  SJTU_USER=xxxxxxx eperson/course-plus-data
```