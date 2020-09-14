from httpx import AsyncClient
from pysjtu import Session as _Session

from .consts import HEADERS


class Session:
    def __init__(self, username: str, password: str):
        self._session = _Session(username, password)
        self.session = AsyncClient(cookies=self._session.cookies, headers=HEADERS)

    async def get(self, url: str, params: dict = None, timeout: int = 5, **kwarg):
        return await self.session.post(url, params=params, timeout=timeout, **kwarg)

    async def post(self, url: str, params: dict = None, data: dict = None, timeout: int = 5, **kwarg):
        return await self.session.post(url, params=params, data=data, timeout=timeout, **kwarg)
