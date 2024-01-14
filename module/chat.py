from typing import Optional
from module import auxiliary
from module import chatgpt
import enum
import bardapi
import re_edge_gpt
import claude2_api
import easy_ernie
import config
import asyncio
import uuid
import json
import dataclasses

CHATS = []

BARD_COOKIE = auxiliary.getCookie('./cookie/bard.json')
with open('./cookie/bing.json', 'r') as file:
    BING_COOKIE = json.load(file)
CLAUDE_COOKIE = auxiliary.getCookie('./cookie/claude.json', dict_=False)
ERNIE_COOKIE = auxiliary.getCookie('./cookie/ernie.json')

class Type(enum.Enum):
    BARD = 'Bard'
    BING = 'Bing'
    CHATGPT = 'ChatGPT'
    CLAUDE = 'Claude'
    ERNIE = 'Ernie'

@dataclasses.dataclass
class Chat:
    type_: Type
    token: str
    bot: object
    parameter: dict
    timestamp: int

async def generate(type_: Type, parameter: dict={}) -> Optional[tuple]:
    global CHATS
    addressPortProxy = f'{config.PROXY["host"]}:{config.PROXY["port"]}' if config.PROXY['enable'] else None
    proxy = {
        'http': f'http://{addressPortProxy}/',
        'https': f'https://{addressPortProxy}/'
    } if config.PROXY['enable'] else None
    if type_ == Type.BARD:
        bot = bardapi.BardCookies(cookie_dict=BARD_COOKIE, proxies=proxy)
    elif type_ == Type.BING:
        bot = await re_edge_gpt.Chatbot.create(proxy=addressPortProxy, cookies=BING_COOKIE)
    elif type_ == Type.CHATGPT:
        bot = chatgpt.ChatGPT(config.CHATGPT_KEY, proxy=proxy)
    elif type_ == Type.CLAUDE:
        claudeSession = claude2_api.SessionData(CLAUDE_COOKIE, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        claudeProxy = claude2_api.client.HTTPProxy(
            config.PROXY['host'],
            config.PROXY['port'],
            use_ssl=config.PROXY['ssl']
        ) if config.PROXY['enable'] else None
        bot = claude2_api.ClaudeAPIClient(claudeSession, proxy=claudeProxy)
        parameter['chatId'] = bot.create_chat()
    elif type_ == Type.ERNIE:
        bot = easy_ernie.FastErnie(ERNIE_COOKIE['BAIDUID'], ERNIE_COOKIE['BDUSS_BFESS'])
    else:
        return None
    token = str(uuid.uuid4())
    CHATS.append(Chat(type_, token, bot, parameter, auxiliary.getTimestamp()))
    return token, bot

def get(type_: Type, token: str) -> Optional[Chat]:
    global CHATS
    for chat in CHATS:
        if chat.type_ == type_ and chat.token == token:
            return chat
    return None

def update(token, parameter: dict) -> None:
    global CHATS
    for chat in CHATS:
        if chat.token == token:
            chat.parameter = parameter
            break

async def check(loop=True) -> None:
    global CHATS
    while True:
        for chat in CHATS.copy():
            if loop and auxiliary.getTimestamp() - chat.timestamp <= config.TOKEN_USE_MAX_TIME_INTERVAL * 60:
                continue

            if chat.type_ == Type.BARD:
                await chat.bot.close()
            elif chat.type_ == Type.BING:
                chat.bot.close()
            elif chat.type_ == Type.CLAUDE:
                chat.bot.delete_chat(chat.parameter['chatId'])
            elif chat.type_ == Type.ERNIE:
                chat.bot.close()
            CHATS.remove(chat)

        if loop:
            await asyncio.sleep(60)
        else:
            break