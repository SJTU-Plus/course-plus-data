import json
import time
from pathlib import Path

from bs4 import BeautifulSoup
from loguru import logger
from requests import session
from tqdm import tqdm

STUDENT_ID = ''
YEAR = 2019
OUTPUT_DIR = Path(f'lesson_description_{YEAR}')

COOKIES = {
    'JSESSIONID': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'kc@i.sjtu.edu.cn': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
}

###############################################################################

client = session()
client.cookies.update(COOKIES)


def timestamp():
    return int(time.time() * 1000)


def check_resp(resp):
    logger.debug(
        f'{resp.request.method} {resp.status_code} {resp.request.url}')
    resp.raise_for_status()


def fetch_plans_index(njdm_id):
    url = f'https://i.sjtu.edu.cn/jxzxjhgl/jxzxjhck_cxJxzxjhckIndex.html'

    resp = client.post(url, params={
        'doType': 'query',
        'gnmkdm': 'N153540',
        'su': STUDENT_ID
    }, data={
        'jg_id': '',
        'njdm_id': njdm_id,
        'dlbs': '',
        'zyh_id': '',
        '_search': False,
        'nd': timestamp(),
        'queryModel.showCount': 5000,
        'queryModel.currentPage': 1,
        'queryModel.sortName': 'bjgs',
        'queryModel.sortOrder': 'desc',
        'time': 8,
    })

    check_resp(resp)
    """
    {
        "bjgs": "49",
        "date": "二○二○年八月七日",
        "dateDigit": "2020年8月7日",
        "dateDigitSeparator": "2020-8-7",
        "day": "7",
        "dlbs": "大类",
        "jg_id": "02000",
        "jgpxzd": "1",
        "jhrs": "1450",
        "jxzxjhxx_id": "A130C60979BB610EE055F8163ED16360",
        "kcs": "58",
        "listnav": "false",
        "localeKey": "zh_CN",
        "month": "8",
        "njdm": "2020",
        "njmc": "2020",
        "pageable": true,
        "queryModel": {
            "currentPage": 1,
            "currentResult": 0,
            "entityOrField": false,
            "limit": 15,
            "offset": 0,
            "pageNo": 0,
            "pageSize": 15,
            "showCount": 10,
            "sorts": [],
            "totalCount": 0,
            "totalPage": 0,
            "totalResult": 0
        },
        "rangeable": true,
        "row_id": "1",
        "rwbj": "班级",
        "sfgazy": "否",
        "totalResult": "150",
        "userModel": {
            "monitor": false,
            "roleCount": 0,
            "roleKeys": "",
            "roleValues": "",
            "status": 0,
            "usable": false
        },
        "xqh_id": "02",
        "xqmc": "闵行",
        "xz": "4",
        "year": "2020",
        "zyfxgs": "0",
        "zyh": "02010011",
        "zyh_id": "02010011",
        "zymc": "工科平台"
    }
    """
    return resp.json().get('items')


def fetch_plans_lesson(jxzxjhxx_id):
    url = 'https://i.sjtu.edu.cn/jxzxjhgl/jxzxjhkcxx_cxJxzxjhkcxxIndex.html'

    resp = client.post(url, params={
        'doType': 'query',
        'gnmkdm': 'N153540',
        'su': STUDENT_ID
    }, data={
        'jyxdxnm': '',
        'jyxdxqm': '',
        'yxxdxnm': '',
        'yxxdxqm': '',
        'shzt': '',
        'kch': '',
        'jxzxjhxx_id': jxzxjhxx_id,
        'xdlx': '',
        '_search': False,
        'nd': timestamp(),
        'queryModel.showCount': 5000,
        'queryModel.currentPage': 1,
        'queryModel.sortName': 'jyxdxnm,jyxdxqm,kch',
        'queryModel.sortOrder': 'asc',
        'time': 3,
    })

    check_resp(resp)
    """
    {
        "sqztmc": "保存",
        "xsdm_01": 48,
        "qsjsz": "无",
        "sfyx": 0,
        "xfyqjd_id": "A1A7FC3FCFC8318EE055F8163ED16360",
        "kch_id": "EN061",
        "kch": "EN061",
        "jcbjmc": "是",
        "zyh_id": "070101",
        "jyxdxqm": "1",
        "kcxzdm": "02",
        "kkbmmc": "外国语学院",
        "xsxxxx": "理论(3.0)",
        "fxbj": "否",
        "exwbj": "否",
        "zymc": "数学与应用数学",
        "zyfxmc": "无方向",
        "sfls": 0,
        "dlmc": "数学与应用数学",
        "kcxzmc": "限选",
        "sflsmc": "未落实",
        "zxbj": "是",
        "xdlx": "zx",
        "jyxdxnm": "2020-2021",
        "sfsjk": "否",
        "yyxdxnxqmc": "2020-2021\/1",
        "zyhxkcbj": "是",
        "zyfx_id": "wfx",
        "sfcj": "否",
        "jxzxjhxx_id": "A1A7FC3FCFAF318EE055F8163ED16360",
        "kclbmc": "公共课程类",
        "kcmc": "大学英语（1）",
        "totalresult": 84,
        "zyzgkcbj": "否",
        "ezybj": "否",
        "jxzxjhkcxx_id": "A1A7FC3FCFCD318EE055F8163ED16360",
        "xf": "3.0",
        "jcbj": "1",
        "nodestatusname": "[]",
        "khfsdm": "考试",
        "zxs": 48,
        "xqmc": "闵行",
        "shzt": "0",
        "xfyqjdmc": "英语选修",
        "row_id": 1
    }
    """
    return resp.json().get('items')


def fetch_lesson_detail(kch_id):
    url = 'https://i.sjtu.edu.cn/jxjhgl/common_cxKcJbxx.html'

    resp = client.get(url, params={
        'id': kch_id,
        'time': int(time.time()*1000),
        'gnmkdm': 'N153540',
        'su': STUDENT_ID
    })

    check_resp(resp)
    return resp.text


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=False)

    lesson_pool = {}

    logger.info(f'开始下载{YEAR}级教学执行计划索引')

    index = fetch_plans_index(YEAR)

    logger.info(f'开始下载教学执行计划')

    for item in tqdm(index):
        jxzxjhxx_id = item.get('jxzxjhxx_id')
        lessons = fetch_plans_lesson(jxzxjhxx_id)
        for lesson in lessons:
            lesson_pool[lesson.get('kch_id')] = lesson.get('kch')

    logger.info(f'开始下载课程详情，大约需要7分钟')

    for kch_id, kch in tqdm(lesson_pool.items()):
        file_path = OUTPUT_DIR/f'{kch}_{kch_id}.html'
        html = fetch_lesson_detail(kch_id)
        file_path.write_text(html, encoding='utf-8')

    (OUTPUT_DIR/f'index.json').write_text(json.dumps(lesson_pool))

    logger.info(f'开始解析课程详情，大约需要2分钟')

    pool = {}
    for p in tqdm(OUTPUT_DIR.glob('*.html')):
        soup = BeautifulSoup(p.read_bytes(), 'html.parser')

        detail = {}

        # parse head

        head = soup.find('table').find('table')
        keys = [td.text.strip() for td in head.find_all('td')]
        values = [th.text.strip() for th in head.find_all('th')]
        detail['meta'] = dict(zip(keys, values))

        # parse home

        panel_home = soup.find('div', id='home')
        home = {}
        [key, val] = panel_home.find('blockquote').text.strip().split('：')
        home[key] = val

        l = []
        trs = panel_home.find('table').find('table').find_all('tr')
        keys = [th.text.strip() for th in trs[0].find_all('th')]
        for tr in trs[1:]:
            values = [td.text.strip() for td in tr.find_all('td')]
            l.append(dict(zip(keys, values)))

        home['学时分项'] = l
        detail['home'] = home

        # parse profile

        panel_profile = soup.find('div', id='profile')
        keys = [td.text.strip() for td in panel_profile.find_all('td')]
        values = [th.text.strip() for th in panel_profile.find_all('th')]
        detail['profile'] = dict(zip(keys, values))

        # parse info

        panel_info = soup.find('div', id='info')
        keys = [td.text.strip() for td in panel_info.find_all('td')]
        values = [th.text.strip() for th in panel_info.find_all('th')]
        detail['info'] = dict(zip(keys, values))

        pool[detail['meta']['课程代码']] = detail

    Path(f'lesson_description_{YEAR}.json').write_text(
        json.dumps(pool, ensure_ascii=False), encoding='UTF-8')
