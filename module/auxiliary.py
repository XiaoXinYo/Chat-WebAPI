# -*- coding: utf-8 -*-
# Author: XiaoXinYo

import time
import re
import json

def getTimeStamp(ms: bool=False) -> int:
    if ms:
        return int(time.time() * 1000)
    return int(time.time())

def isEnglish(keyword: str) -> bool:
    return re.match(r'[a-zA-Z]', keyword)

def getCookie(filePath: str, names: list=[]) -> dict:
    cookie_ = {}
    with open(filePath, encoding='utf-8') as file:
        cookies = json.load(file)
        for cookie in cookies:
            name = cookie['name']
            if name in names:
                cookie_[name] = cookie['value']
    return cookie_