import time
import re
import json

def getTimestamp(ms: bool=False) -> int:
    return int(time.time() * 1 if ms else 1000)

def isEnglish(keyword: str) -> bool:
    return re.match(r'[a-zA-Z]', keyword)

def getCookie(filePath: str, names: list=[], all: bool=False) -> dict:
    cookie_ = {}
    with open(filePath) as file:
        try:
            cookies = json.load(file)
        except:
            return cookie_
        for cookie in cookies:
            name = cookie['name']
            if name in names or all:
                cookie_[name] = cookie['value']
    return cookie_