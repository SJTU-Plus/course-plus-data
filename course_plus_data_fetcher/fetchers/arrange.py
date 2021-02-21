import asyncio
import logging
import time
from argparse import ArgumentParser, Namespace
from functools import reduce
from typing import List, Optional

from httpx import ReadTimeout

from .base import Fetcher
from ..consts import TRIMESTER_MAP
from ..session import Session


class ArrangeFetcher(Fetcher):
    @staticmethod
    def set_argparse(parser: ArgumentParser):
        parser.add_argument("year", type=int)
        parser.add_argument("trimester", type=int)
        parser.add_argument("page_size", type=int, default=3000)

    def __init__(self, session: Session, args: Namespace):
        super().__init__(session, args)

        self.year: int = args.year
        self.trimester_display: int = args.trimester
        self.trimester: int = TRIMESTER_MAP[self.trimester_display]
        self.page_size: int = args.page_size

        self.session = session

    async def _get_data(self, year: int, trimester: int, page_size: int, page_num: int = 1,
                        weekday: Optional[int] = None) -> dict:
        func_label = f"Query(year={year}, trimester={trimester}, weekday={weekday}," \
                     f" page_size={page_size}, page_num={page_num})"
        payload = {
            "xnm": year,
            "xqm": trimester,
            "nd": int(time.time() * 1000),
            **({"xqj": weekday} if weekday else {}),
            "queryModel.showCount": page_size,
            "queryModel.currentPage": page_num,
            "queryModel.sortName": "",
            "queryModel.sortOrder": "asc",
        }
        params = {"func_widget_guid": "DA1B5BB30E1F4CB99D1F6F526537777B",
                  "gnmkdm": "N219904"}

        resp = None
        while not resp:
            try:
                resp = await self.session.post("https://i.sjtu.edu.cn/design/funcData_cxFuncDataList.html",
                                               params=params, data=payload, timeout=120)
            except ReadTimeout:
                logging.error(
                    f'{func_label} timeout. Retrying.')

        logging.info(f'{func_label} success.')
        return resp.json()

    async def _get_general_course_data(self, year: int, trimester: int, page_size: int, page_num: int = 1) -> dict:
        func_label = f"Query(year={year}, trimester={trimester}," \
                     f" page_size={page_size}, page_num={page_num})"
        payload = {
            "xnm": year,
            "xqm": trimester,
            "nd": int(time.time() * 1000),
            "sftsk": "是",
            "queryModel.showCount": page_size,
            "queryModel.currentPage": page_num,
            "queryModel.sortName": "",
            "queryModel.sortOrder": "asc",
        }
        params = {"func_widget_guid": "8B04B7BBB49C4455E0530200A8C06482",
                  "gnmkdm": "N2199113"}

        resp = None
        while not resp:
            try:
                resp = await self.session.post("https://i.sjtu.edu.cn/design/funcData_cxFuncDataList.html",
                                               params=params, data=payload, timeout=120)
            except ReadTimeout:
                logging.error(
                    f'{func_label} timeout. Retrying.')

        logging.info(f'{func_label} success.')
        return resp.json()

    async def _get_length(self) -> int:
        return (await self._get_data(self.year, self.trimester, 1))["totalCount"]

    async def _get_general_length(self) -> int:
        return (await self._get_general_course_data(self.year, self.trimester, 1))["totalCount"]

    async def fetch(self) -> List[dict]:
        logging.info(f"Fetching: Year {self.year} TRIMESTER {self.trimester_display}")

        logging.info("Checking data length.")
        item_count = await self._get_length()
        general_item_count = await self._get_general_length()
        logging.info(f"Data length: {item_count}, general courses: {general_item_count}")

        logging.info("Fetching data.")
        raw_data = await asyncio.gather(*(self._get_data(self.year, self.trimester, self.page_size, 1, weekday)
                                          for weekday in range(1, 8)))
        general_data = await self._get_general_course_data(self.year, self.trimester, self.page_size, 1)
        lesson_data = reduce(lambda x, y: (x if x else []) + y, map(lambda x: x["items"], raw_data))

        if len(lesson_data) != item_count:
            logging.warning("Expected list length and received list length don't match.")
        if len(general_data) != general_item_count:
            logging.warning("Expected general list length and received general list length don't match.")

        general_data = {lesson['jxb_id']: lesson for lesson in general_data["items"]}
        for lesson in lesson_data:
            if lesson['jxb_id'] in general_data:
                lesson['kzmc'] = general_data[lesson['jxb_id']]['kzmc']
            else:
                lesson['kzmc'] = ""

        return lesson_data
