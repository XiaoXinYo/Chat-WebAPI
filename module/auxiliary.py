from typing import Union
import time
import json

def getTimestamp(ms: bool=False) -> int:
    return int(time.time() * (1000 if ms else 1))

def getCookie(filePath: str, dict_: bool=True) -> Union[dict, str]:
    result = {}
    with open(filePath) as file:
        try:
            cookies = json.load(file)
        except:
            return result

        for cookie in cookies:
            result[cookie['name']] = cookie['value']

    if not dict_:
        result = '; '.join([f'{name}={value}' for name, value in result.items()])
    return result