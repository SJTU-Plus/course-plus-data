#/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import asyncio
import logging
import json

from .fetchers.base import fetchers
from .fetchers.func import create_fetcher, get_default_args,SJTU_login
from .fetchers.session import FetchSession

logging.basicConfig(level=logging.INFO)

async def fetch(args: argparse.Namespace,session:FetchSession):
    
    fetcher = create_fetcher(args.fetcher, session, args)
    if fetcher is None:
        logging.error("Fetcher not found.")
        return

    data = await fetcher.fetch()

    logging.info(f"Writing to {args.output_file}.")
    with open(args.output_file,'w') as f:
        json.dump(data,f,indent=1,ensure_ascii=False)
    logging.info(f"Fetcher:{args.fetcher} Done.")

async def auto_fetch():
    session=await SJTU_login()
    if(session is None):
        logging.error("Login Failed.")
        return
    else:
            for name in fetchers.keys():
                await fetch(get_default_args(name),session)
            logging.info("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Course plus data fetching utility.")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(auto_fetch())