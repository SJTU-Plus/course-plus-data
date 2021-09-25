import logging
import os

from argparse import Namespace
from time import localtime,time
from pysjtu.exceptions import LoginException, SessionException

from .base import fetchers 
from .session import FetchSession
from .consts import FILEPATH

SJTU_USER = os.environ.get("SJTU_USER", None)
SJTU_PASS = os.environ.get("SJTU_PASS", None)
logging.basicConfig(level=logging.INFO)

async def SJTU_login():

    if not SJTU_USER or not SJTU_PASS:
        logging.error("Missing SJTU_USER or SJTU_PASS.")
        return None
    logging.info("Logging into SJTU.")
    try:
        session = FetchSession(SJTU_USER, SJTU_PASS)
    except (LoginException, SessionException):
        logging.exception("Error occur when logging.")
        return None
    return session

def create_fetcher(name: str, session: FetchSession, args: Namespace):
    cls = fetchers.get(name)
    if not cls:
        return None
    return cls(session, args)

def get_default_args(name)->Namespace:

        dic={}
        t=localtime(time())
        y=t[0]
        m=t[1]
        dic['fetcher']=name
        dic['page_size']=10000
        if(name=='arrange'): 
                s=0

                if m==1:
                        y-=1
                        s=1
                elif m>=2 and m<=5:
                        y-=1
                        s=2
                elif m>=6 and m<=7:
                        y-=1
                        s=3
                elif m>=8 and m<=12:
                        s=1

                dic['trimester']=s
                dic['year']=y
                dic['output_file']=FILEPATH+f"lessonData_{y}-{y+1}_{s}.json"
        elif(name=='description'):
                dic['output_file']=FILEPATH+f'lesson_description_{y}.json'
                dic['year']=y
        elif(name=='conversion'):
                dic['output_file']=FILEPATH+f'lesson_conversion_{y}.json'

        return Namespace(**dic)

