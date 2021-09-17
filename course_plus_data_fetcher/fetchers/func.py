from argparse import Namespace
import asyncio
import json
import re
import typing
from time import localtime,time
import logging

from .base import fetchers 
from .session import FetchSession

logging.basicConfig(level=logging.INFO)

async def process_json(obj:typing.Dict,filename:str):
    for key in range(len(obj)):
        for data_key in obj[key].keys():
            if data_key == 'xkbz' and isinstance(obj[key][data_key], str):
                raw_content = obj[key][data_key]
                obj[key][data_key] = re.sub(r'([0-9]{7,})', 'XXXXXXXX', raw_content)
    with open(filename,'w') as f:
        json.dump(obj,f,indent=1,ensure_ascii=False)

def create_fetcher(name: str, session: FetchSession, args: Namespace):
    cls = fetchers.get(name)
    if not cls:
        return None
    return cls(session, args)

def get_default_args()->Namespace:
        dic={}
        dic['fetcher']='arrange'
        dic['page_size']=10000

        t=localtime(time())
        y=t[0]
        m=t[1]
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

        dic['year']=y
        dic['trimester']=s
        filename=f"lessonData_{y}-{y+1}_{s}.json"
        dic['output_file']=filename
        
        return Namespace(**dic)