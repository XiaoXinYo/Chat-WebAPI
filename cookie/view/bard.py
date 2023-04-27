# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from fastapi import APIRouter, Request, Response
from module import core, auxiliary
import asyncio
from Bard import Chatbot
import uuid
import json
import re

BardAPP = APIRouter()
CHATBOT = {}

async def checkToken() -> None:
    global CHATBOT
    while True:
        for token in CHATBOT.copy():
            chatBot = CHATBOT[token]
            if auxiliary.getTimeStamp() - chatBot.get('useTimeStamp') > 5 * 60:
                del chatBot
        await asyncio.sleep(60)

def getChatBot(token: str) -> tuple:
    global CHATBOT
    if token in CHATBOT:
        chatBot = CHATBOT[token]['chatBot']
        CHATBOT[token]['useTimeStamp'] = auxiliary.getTimeStamp()
    else:
        chatBot = Chatbot(auxiliary.getCookie('./cookie/bard.json', '__Secure-1PSID').get('__Secure-1PSID'))
        token = str(uuid.uuid4())
        CHATBOT[token] = {}
        CHATBOT[token]['chatBot'] = chatBot
        CHATBOT[token]['useTimeStamp'] = auxiliary.getTimeStamp()
    return token, chatBot

@BardAPP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    elif not auxiliary.isEnglish(question):
        return core.GenerateResponse().error(110, '仅支持英文')
    
    token, chatBot = getChatBot(token)
    if not chatBot:
        return core.GenerateResponse().error(120, 'token不存在')
    data = chatBot.ask(question)

    answer = data.get('content')
    url = json.dumps(data.get('factualityQueries'))
    urls = re.findall(r'"(http.*?)"',url)
    
    return core.GenerateResponse().success({
        'answer': answer,
        'urls': urls,
        'token': token
    })