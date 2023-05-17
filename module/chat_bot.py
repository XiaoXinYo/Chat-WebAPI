# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from typing import Union
from module import auxiliary
import Bard
import EdgeGPT
import revChatGPT.V3
import easy_ernie
import config
import asyncio
import uuid

CHAT_BOT = {}

def generateChatBot(type_: str) -> Union[tuple, None]:
    global CHAT_BOT
    token = str(uuid.uuid4())
    if type_ == 'Bard':
        chatBot = Bard.Chatbot(auxiliary.getCookie('./cookie/bard.json', ['__Secure-1PSID'])['__Secure-1PSID'], proxy=config.PROXY)
    elif type_ == 'Bing':
        chatBot = EdgeGPT.Chatbot(proxy=config.PROXY, cookie_path='./cookie/bing.json')
    elif type_ == 'ChatGPT':
        chatBot = revChatGPT.V3.Chatbot(config.CHATGPT_KEY, proxy=config.PROXY)
    elif type_ == 'Ernie':
        cookie = auxiliary.getCookie('./cookie/ernie.json', ['BAIDUID', 'BDUSS_BFESS'])
        chatBot = easy_ernie.FastErnie(cookie['BAIDUID'], cookie['BDUSS_BFESS'])
    else:
        return None
    CHAT_BOT[token] = {}
    CHAT_BOT[token]['type'] = type_
    CHAT_BOT[token]['chatBot'] = chatBot
    CHAT_BOT[token]['useTimeStamp'] = auxiliary.getTimeStamp()
    return token, chatBot

def getChatBot(token: str) -> Union[dict, None]:
    global CHAT_BOT
    if token in CHAT_BOT:
        CHAT_BOT[token]['useTimeStamp'] = auxiliary.getTimeStamp()
        return CHAT_BOT[token]
    return None

async def checkChatBot() -> None:
    global CHAT_BOT
    while True:
        for token in CHAT_BOT.copy():
            chatBot = CHAT_BOT[token]
            if auxiliary.getTimeStamp() - chatBot['useTimeStamp'] > config.TOKEN_USE_MAX_TIME_INTERVAL * 60:
                if chatBot['type'] == 'Bing':
                    await chatBot['chatBot'].close()
                elif chatBot['type'] == 'Ernie':
                    chatBot['chatBot'].close()
                del chatBot
        await asyncio.sleep(60)