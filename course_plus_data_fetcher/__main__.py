#/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import asyncio
import logging
import os

from pysjtu.exceptions import LoginException, SessionException

from .fetchers.base import fetchers
from .fetchers.func import create_fetcher, get_default_args,process_json
from .fetchers.session import FetchSession

logging.basicConfig(level=logging.INFO)

SJTU_USER = os.environ.get("SJTU_USER", None)
SJTU_PASS = os.environ.get("SJTU_PASS", None)

async def main(args: argparse.Namespace):
    if not SJTU_USER or not SJTU_PASS:
        logging.error("Missing SJTU_USER or SJTU_PASS.")
        return

    logging.info("Logging into SJTU.")
    try:
        session = FetchSession(SJTU_USER, SJTU_PASS)
    except (LoginException, SessionException):
        logging.exception("Error occur when logging.")
        return

    fetcher = create_fetcher(args.fetcher, session, args)
    if fetcher is None:
        logging.error("Fetcher not found.")
        return

    data = await fetcher.fetch()

    logging.info(f"Writing to {args.output_file}.")
    await process_json(data,args.output_file)
    logging.info("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Course plus data fetching utility.")
    parser.add_argument("--output_file", help="Specify output filename.", required=False)
    subparsers = parser.add_subparsers(help="Available fetchers.", dest="fetcher", required=False)
    for name, cls in fetchers.items():
            subparser = subparsers.add_parser(name)
            cls.set_argparse(subparser)
    args=parser.parse_args()
    if not args.fetcher or not args.output_file:
        args=get_default_args()
    asyncio.run(main(args))
