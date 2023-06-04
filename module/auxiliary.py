# -*- coding: utf-8 -*-
# Author: XiaoXinYo

import time
import re
import json
from typing import Match


def getTimeStamp(ms: bool = False) -> int:
    if ms:
        return int(time.time() * 1000)
    return int(time.time())


def isEnglish(keyword: str) -> Match[str] | None:
    return re.match(r'[a-zA-Z]', keyword)


def getCookie(filePath: str, names: list = []) -> dict:
    cookie_ = {}
    if isEmpty(filePath):
        return cookie_
    try:
        with open(filePath) as file:
            cookies = json.load(file)
            for cookie in cookies:
                name = cookie['name']
                if name in names:
                    cookie_[name] = cookie['value']
    except Exception:
        pass

    return cookie_


def isEmpty(filePath: str) -> bool:
    f = open(filePath)
    text = f.read()
    if text == "":
        return True
    else:
        return False
