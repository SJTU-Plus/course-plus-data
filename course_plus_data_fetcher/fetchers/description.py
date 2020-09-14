import asyncio
import logging
import time
from argparse import ArgumentParser, Namespace
from functools import reduce
from typing import List

# noinspection PyProtectedMember
from bs4 import BeautifulSoup, Tag

from .base import Fetcher
from ..session import Session


class DescriptionFetcher(Fetcher):
    @staticmethod
    def set_argparse(parser: ArgumentParser):
        parser.add_argument("year", type=int)

    def __init__(self, session: Session, args: Namespace):
        super().__init__(session, args)

        self.year: int = args.year

        self.session = session

    async def _get_index(self, year: int):
        url = "https://i.sjtu.edu.cn/jxzxjhgl/jxzxjhck_cxJxzxjhckIndex.html"
        payload = {
            'jg_id': '',
            'njdm_id': year,
            'dlbs': '',
            'zyh_id': '',
            '_search': False,
            'nd': int(time.time() * 1000),
            'queryModel.showCount': 5000,
            'queryModel.currentPage': 1,
            'queryModel.sortName': 'bjgs',
            'queryModel.sortOrder': 'desc',
            'time': 0,
        }
        params = {
            "doType": "query",
            'gnmkdm': 'N153540'
        }

        r = await self.session.post(url, params=params, data=payload)
        items = r.json()["items"]
        return [item["jxzxjhxx_id"] for item in items]

    async def _get_lessons(self, plan_id: str):
        url = "https://i.sjtu.edu.cn/jxzxjhgl/jxzxjhkcxx_cxJxzxjhkcxxIndex.html"
        payload = {
            'jyxdxnm': '',
            'jyxdxqm': '',
            'yxxdxnm': '',
            'yxxdxqm': '',
            'shzt': '',
            'kch': '',
            'jxzxjhxx_id': plan_id,
            'xdlx': '',
            '_search': False,
            'nd': int(time.time() * 1000),
            'queryModel.showCount': 5000,
            'queryModel.currentPage': 1,
            'queryModel.sortName': 'jyxdxnm,jyxdxqm,kch',
            'queryModel.sortOrder': 'asc',
            'time': 3,
        }
        params = {
            'doType': 'query',
            'gnmkdm': 'N153540'
        }

        r = await self.session.post(url, params=params, data=payload)
        items = r.json()["items"]
        return {item["kch"]: item["kch_id"] for item in items}

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
            f = lambda x: [item.text.strip() for item in e.find_all(x)]
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
        logging.info(f"Fetching: Year {self.year}")

        logging.info("Fetching index.")
        indexes = await self._get_index(self.year)

        logging.info("Fetching plans.")
        raw_lessons = await asyncio.gather(*(self._get_lessons(index) for index in indexes))
        lessons = reduce(lambda x, y: {**(x if x else {}), **y}, raw_lessons)

        logging.info("Fetching details.")
        raw_details = await asyncio.gather(*(self._get_detail(lesson_id) for lesson_id in lessons.values()))

        logging.info("Parsing details.")
        details = list(map(self._parse_detail, raw_details))
        output = {detail["meta"]["课程代码"]: detail for detail in details}

        return output
