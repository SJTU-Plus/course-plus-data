from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Dict, Type

from ..session import Session


class Fetcher(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        fetchers[cls.__name__.replace("Fetcher", "").lower()] = cls

    @abstractmethod
    def __init__(self, session: Session, args: Namespace): ...

    @abstractmethod
    async def fetch(self): ...

    @staticmethod
    @abstractmethod
    def set_argparse(parser: ArgumentParser): ...


fetchers: Dict[str, Type[Fetcher]] = {}
