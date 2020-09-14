from argparse import Namespace
from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules

from pysjtu import Session

from .base import fetchers

package_dir = Path(__file__).resolve().parent
for (_, module_name, _) in iter_modules([package_dir]):
    module = import_module(f"{__name__}.{module_name}")


def create_fetcher(name: str, session: Session, args: Namespace):
    cls = fetchers.get(name)
    if not cls:
        return None
    return cls(session, args)
