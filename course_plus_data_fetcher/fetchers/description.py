import asyncio
import json
import logging
import time
from argparse import ArgumentParser, Namespace
from functools import reduce
from typing import List

# noinspection PyProtectedMember
from bs4 import BeautifulSoup, Tag

from .base import Fetcher
from ..session import Session


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


class DescriptionFetcher(Fetcher):
    @staticmethod
    def set_argparse(parser: ArgumentParser):
        parser.add_argument("input_file", type=str)

    def __init__(self, session: Session, args: Namespace):
        super().__init__(session, args)

        self.input_file: str = args.input_file
        self.output_file: str = args.output_file

        self.filter: List[str] = ['研究生院', '体育系']

        self.session = session

    async def _get_detail(self, lesson_id: str):
        url = 'https://i.sjtu.edu.cn/jxjhgl/common_cxKcJbxx.html'
        params = {
            'id': lesson_id,
            'time': int(time.time() * 1000),
            'gnmkdm': 'N153540'
        }

        r = await self.session.get(url, params=params)

        return r.text

    @staticmethod
    def _parse_detail(src: str):
        def _parse_kv(e: Tag):
            def f(x): return [item.text.strip() for item in e.find_all(x)]
            return {k: v for k, v in zip(f("td"), f("th"))}

        def _parse_home(e: Tag):
            def _parse_subfield(keys: List[str], e: Tag):
                values = [td.text.strip() for td in e.find_all("td")]
                return {k: v for k, v in zip(keys, values)}

            [k, v] = e.find("blockquote").text.strip().split("：")

            subfield_trs = panel_home.find('table').find('table').find_all('tr')
            subfield_keys = [th.text.strip() for th in subfield_trs[0].find_all('th')]
            subfields = [_parse_subfield(subfield_keys, tr) for tr in subfield_trs[1:]]

            return {
                k: v,
                "学时分项": subfields
            }

        soup = BeautifulSoup(src, 'html.parser')
        head = soup.find('table').find('table')
        panel_home = soup.find('div', id='home')
        panel_profile = soup.find('div', id='profile')
        panel_info = soup.find('div', id='info')

        detail = {
            "meta": _parse_kv(head),
            "home": _parse_home(panel_home),
            "profile": _parse_kv(panel_profile),
            "info": _parse_kv(panel_info)
        }
        return detail

    async def fetch(self) -> dict:
        logging.info(f"Fetching: Input file {self.input_file}")

        logging.info("Loading existing.")
        with open(self.output_file, mode="r") as f:
            output = json.load(f)

        logging.info("Loading lessons.")
        with open(self.input_file, mode="r") as f:
            lessons = {}
            for lesson in json.load(f):
                if lesson['kch'] not in output and lesson['kkxy'] not in self.filter:
                    lessons[lesson['kch']] = lesson['kch_id']

        logging.info("Fetching details.")
        raw_details = await gather_with_concurrency(100, *(self._get_detail(lesson_id) for lesson_id in lessons.values()))

        logging.info("Parsing details.")
        details = list(map(self._parse_detail, raw_details))
        output.update({detail["meta"]["课程代码"]: detail for detail in details})

        return output
