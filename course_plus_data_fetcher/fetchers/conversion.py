import asyncio
import logging
import time
from argparse import ArgumentParser, Namespace
from functools import reduce
from typing import List
from httpx import ReadTimeout

from .base import Fetcher
from .session import FetchSession


class ConversionFetcher(Fetcher):
    @staticmethod
    def set_argparse(parser: ArgumentParser):
        parser.add_argument("page_size", type=int, default=3000)

    def __init__(self, session: FetchSession, args: Namespace):
        super().__init__(session, args)
        self.page_size: int = args.page_size

        self.session = session

    async def _get_data(self, page_size: int, page_num: int = 1) -> dict:
        func_label = f"Query(page_size={page_size}, page_num={page_num})"
        payload = {
            "nd": int(time.time() * 1000),
            "queryModel.showCount": page_size,
            "queryModel.currentPage": page_num,
            "queryModel.sortName": "xh asc ,thkcid,tkkcid",
            "queryModel.sortOrder": "asc",
            "jg_id" : "",
            "kch": "",
            "tybj": "",
            "kcglbm_id": ""
        }
        params = {
            'doType': 'query',
            'gnmkdm': 'N151505'
        }

        resp = None
        while not resp:
            try:
                resp = await self.session.post("https://i.sjtu.edu.cn/kcthgl/kcthxxwh_cxKcthjbxxIndex.html",
                                               params=params, data=payload, timeout=120)
            except ReadTimeout:
                logging.error(
                    f'{func_label} timeout. Retrying.')

        logging.info(f'{func_label} success.')
        return resp.json()

    async def _get_length(self) -> int:
        return (await self._get_data(1))["totalCount"]

    async def fetch(self) -> List[dict]:
        logging.info(f"Fetching")

        logging.info("Checking data length.")
        item_count = await self._get_length()
        logging.info(f"Data length: {item_count}")

        logging.info("Fetching data.")
        lesson_data = await self._get_data(self.page_size, 1)

        if len(lesson_data) != item_count:
            logging.warning("Expected list length and received list length don't match.")

        return {lesson["thkch"]: lesson["tkkch"] for lesson in lesson_data["items"]}
