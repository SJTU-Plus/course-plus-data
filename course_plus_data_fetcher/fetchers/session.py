from httpx import AsyncClient
from pysjtu import Session as SJTUSession
from .consts import HEADERS


class FetchSession:
    def __init__(self, username: str, password: str):
        self._account_session = SJTUSession(username, password)
        self._fetch_session = AsyncClient(cookies=self._account_session.cookies, headers=HEADERS,verify=True)
    async def get(self, url: str, params: dict = None, timeout: int = 500, **kwarg):
        return await self._fetch_session.get(url, params=params, timeout=timeout, **kwarg)
    async def post(self, url: str, params: dict = None, data: dict = None, timeout: int = 500, **kwarg):
        return await self._fetch_session.post(url,params=params,data=data,timeout=timeout,**kwarg)
