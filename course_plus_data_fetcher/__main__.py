import argparse
import asyncio
import json
import logging
import os

from pysjtu.exceptions import LoginException, SessionException

from .fetchers import create_fetcher, fetchers
from .session import Session

logging.basicConfig(level=logging.INFO)

SJTU_USER = os.environ.get("SJTU_USER", None)
SJTU_PASS = os.environ.get("SJTU_PASS", None)


async def main(args: argparse.Namespace):
    if not SJTU_USER or not SJTU_PASS:
        logging.error("Missing SJTU_USER or SJTU_PASS.")
        return

    logging.info("Logging into SJTU.")
    try:
        session = Session(SJTU_USER, SJTU_PASS)
    except (LoginException, SessionException):
        logging.exception("Error occur when logging.")
        return

    fetcher = create_fetcher(args.fetcher, session, args)
    if fetcher is None:
        logging.error("Fetcher not found.")
        return

    data = await fetcher.fetch()

    logging.info(f"Writing to {args.output_file}.")
    with open(args.output_file, mode="w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    logging.info("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Course plus data fetching utility.")
    parser.add_argument("--output_file", help="Specify output filename.", required=True)
    subparsers = parser.add_subparsers(help="Available fetchers.", dest="fetcher", required=True)
    for name, cls in fetchers.items():
        subparser = subparsers.add_parser(name)
        cls.set_argparse(subparser)

    asyncio.run(main(parser.parse_args()))
