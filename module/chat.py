from typing import Optional
from module import auxiliary
from module import chatgpt
import enum
import bardapi
import easy_ernie
import config
import asyncio
import uuid

CHAT = {}

BARD_COOKIE = auxiliary.getCookie('./cookie/bard.json', all=True)
ERNIE_COOKIE = auxiliary.getCookie('./cookie/ernie.json', names=['BAIDUID', 'BDUSS_BFESS'])

class Type(enum.Enum):
    BARD = 'Bard'
    CHATGPT = 'ChatGPT'
    ERNIE = 'Ernie'

class Chat:
    type_: Type
    bot: object
    parameter: dict
    timestamp: int

    def __init__(self, type_: Type, bot: object, timestamp: int, parameter: dict=None) -> None:
        self.type_ = type_
        self.bot = bot
        self.parameter = parameter
        self.timestamp = timestamp

def generate(type_: Type, parameter: dict=None) -> Optional[tuple]:
    global CHAT
    token = str(uuid.uuid4())
    proxy = {
        'http': f'http://{config.PROXY}/',
        'https': f'https://{config.PROXY}/'
    } if config.PROXY else None
    if type_ == Type.BARD:
        bot = bardapi.BardCookies(cookie_dict=BARD_COOKIE, proxies=proxy)
    elif type_ == Type.CHATGPT:
        bot = chatgpt.ChatGPT(config.CHATGPT_KEY, proxy=proxy)
    elif type_ == Type.ERNIE:
        bot = easy_ernie.FastErnie(ERNIE_COOKIE['BAIDUID'], ERNIE_COOKIE['BDUSS_BFESS'])
    else:
        return None
    CHAT[token] = Chat(type_, bot, auxiliary.getTimestamp(), parameter=parameter)
    return token, bot

def get(token: str) -> Optional[Chat]:
    global CHAT
    if token in CHAT:
        CHAT[token].timestamp = auxiliary.getTimestamp()
        return CHAT[token]
    return None

def update(token, parameter: dict) -> None:
    global CHAT
    if token in CHAT:
        CHAT[token].parameter = parameter

async def check(loop=True) -> None:
    global CHAT
    while True:
        for token in CHAT.copy():
            chat = CHAT[token]
            if auxiliary.getTimestamp() - chat.timestamp > config.TOKEN_USE_MAX_TIME_INTERVAL * 60:
                if chat.type_ == Type.BARD:
                    await chat.bot.close()
                elif chat.type_ == Type.ERNIE:
                    chat.bot.close()
                del CHAT[token]
        if loop:
            await asyncio.sleep(60)
        else:
            break