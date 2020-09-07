import asyncio
import json
from functools import reduce
from math import ceil
from time import time
from django.template.base import kwarg_re
from numpy.core.defchararray import less
from tqdm import tqdm
from loguru import logger
from requests import session

# 在此填入i.sjtu.edu.cn的cookies
cookies = {
    'JSESSIONID': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'kc@i.sjtu.edu.cn': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
}

# 在此填入学年和学期(1:秋季学期，2:春季学期，3:夏季小学期)
ACADEMIC_YEAR: str = '2020-2021'
SEMESTER: int = 1

FILENAME: str = 'lessonData_{}_{}.json'.format(ACADEMIC_YEAR, SEMESTER)


def timestamp():
    return int(time() * 1000)


def check_resp(resp):
    logger.debug(f'{resp.request.method} {resp.status_code} {resp.request.url}')
    resp.raise_for_status()
    return resp


# 功能模块：按条件查询上课情况
_SEMESTER_MAP = {1: '3', 2: '12', 3: '16'}
_REQUEST_URL = 'https://i.sjtu.edu.cn/design/funcData_cxFuncDataList.html?func_widget_guid=DA1B5BB30E1F4CB99D1F6F526537777B&gnmkdm=N219904'

s = session()
s.cookies.update(cookies)
s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
s.headers['Referer'] = 'https://i.sjtu.edu.cn/design/viewFunc_cxDesignFuncPageIndex.html?gnmkdm=N219904&layout=default'


def get_data(academic_year: str, semester: int, page_size: int, page_num: int = 1, xqj=-1):
    logger.debug(f'Query(academic_year={academic_year}, semester={semester}, xqj={xqj}, page_size={page_size}, page_num={page_num})')

    begin = time()
    form = {
        'xnm': academic_year[:4],
        'xqm': _SEMESTER_MAP[semester],
        'nd': timestamp(),
        'queryModel.showCount': str(page_size),  # 最大获取数
        'queryModel.currentPage': str(page_num),
        'queryModel.sortName': '',
        'queryModel.sortOrder': 'asc'
    }

    if xqj > 0:
        form['xqj'] = xqj

    resp = s.post(_REQUEST_URL, data=form)

    elapsed = ceil(time() - begin)
    logger.info(f'Query(academic_year={academic_year}, semester={semester}, xqj={xqj}, page_size={page_size}, page_num={page_num}) -> {elapsed} seconds')

    return check_resp(resp)


async def main():
    logger.info('当前任务：{}学年第{}学期'.format(ACADEMIC_YEAR, SEMESTER))
    logger.info('正在获取测试数据，大约需要5秒，请等待')

    resp = get_data(ACADEMIC_YEAR, SEMESTER, 15)
    lesson_data = resp.json()['items']

    if len(lesson_data) == 15:
        logger.info('测试成功，数据长度符合预期')
    else:
        raise Exception(f'测试失败，数据长度不匹配，期望15，实际{len(lesson_data)}')

    ##########

    total_count = resp.json()['totalCount']
    logger.info(f'共有{total_count}条记录。正在请求数据，大约需要3分钟，请耐心等待')

    loop = asyncio.get_event_loop()

    future_pool = [
        loop.run_in_executor(None, get_data, ACADEMIC_YEAR, SEMESTER, 5000, 1, i)
        for i in range(1, 8)
    ]

    lesson_data = []

    for future in tqdm(future_pool):
        resp = await future
        lesson_data += resp.json()['items']

    with open(FILENAME, "w", encoding='utf8') as f:
        json.dump(lesson_data, f, ensure_ascii=False)

    assert total_count == len(lesson_data)
    logger.info('《{}学年第{}学期课程信息》已经成功保存至文件"{}"，共包含课程{}门'.format(ACADEMIC_YEAR, SEMESTER, FILENAME, len(lesson_data)))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
