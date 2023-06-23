import json
import time
from pathlib import Path

from bs4 import BeautifulSoup
from loguru import logger
from requests import session
from tqdm import tqdm

STUDENT_ID = ''
# 在此填入学年和学期(1:秋季学期，2:春季学期，3:夏季小学期)
ACADEMIC_YEAR: str = '2022-2023'
SEMESTER: int = 3
OUTPUT_DIR = Path(f'lesson_description_{ACADEMIC_YEAR}_{SEMESTER}')

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

    logger.info('开始读取课程详情')

    with open('lesson_description_2020.json', 'r', encoding='utf-8') as f:
        pool = json.load(f)
    with open('lesson_conversion.json', 'r', encoding='utf-8') as f:
        conversion = json.load(f)

    lesson_pool = {}

    logger.info(f'开始读取{ACADEMIC_YEAR}学年第{SEMESTER}学期课程信息')

    with open(f'lessonData_{ACADEMIC_YEAR}_{SEMESTER}.json', 'r', encoding='utf-8') as f:
        lessons = json.load(f)
        for lesson in lessons:
            if lesson['kch'] in conversion:
                lesson['kch'] = conversion[lesson['kch']]
            if lesson['kch'] not in pool and lesson['kkxy'] not in ['研究生院', '体育系']:
                lesson_pool[lesson['kch_id']] = lesson['kch']

    logger.info(f'开始下载课程详情')

    for kch_id, kch in tqdm(lesson_pool.items()):
        file_path = OUTPUT_DIR/f'{kch}_{kch_id}.html'
        html = fetch_lesson_detail(kch_id)
        file_path.write_text(html, encoding='utf-8')

    (OUTPUT_DIR/f'index.json').write_text(json.dumps(lesson_pool))

    logger.info(f'开始解析课程详情')

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

    Path('lesson_description_2020.json').write_text(
        json.dumps(pool, ensure_ascii=False), encoding='UTF-8')
