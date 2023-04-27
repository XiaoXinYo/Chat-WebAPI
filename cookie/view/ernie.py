# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from typing import Generator
from fastapi import APIRouter, Request, Response
from module import core, auxiliary
import asyncio
from easy_ernie import FastErnie
import uuid
from fastapi.responses import StreamingResponse

ERNIE_APP = APIRouter()
CHATBOT = {}

async def checkToken() -> None:
    global CHATBOT
    while True:
        for token in CHATBOT.copy():
            chatBot = CHATBOT[token]
            if auxiliary.getTimeStamp() - chatBot.get('useTimeStamp') > 5 * 60:
                chatBot.get('chatBot').close()
                del chatBot
        await asyncio.sleep(60)

def getChatBot(token: str) -> tuple:
    global CHATBOT
    if token:
        if token in CHATBOT:
            chatBot = CHATBOT.get(token).get('chatBot')
        else:
            return token, None
    else:
        cookie = auxiliary.getCookie('./cookie/ernie.json', ['BAIDUID', 'BDUSS_BFESS'])
        chatBot = FastErnie(cookie.get('BAIDUID'), cookie.get('BDUSS_BFESS'))
        token = str(uuid.uuid4())
        CHATBOT[token] = {}
        CHATBOT[token]['chatBot'] = chatBot
    CHATBOT[token]['useTimeStamp'] = auxiliary.getTimeStamp()
    return token, chatBot

@ERNIE_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    
    token, chatBot = getChatBot(token)
    if not chatBot:
        return core.GenerateResponse().error(120, 'token不存在')
    data = chatBot.ask(question)

    return core.GenerateResponse().success({
        'answer': data.get('answer'),
        'urls': data.get('urls'),
        'token': token
    })

@ERNIE_APP.route('/ask_stream', methods=['GET', 'POST'])
async def askStream(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    
    token, chatBot = getChatBot(token)
    if not chatBot:
        return core.GenerateResponse().error(120, 'token不存在')
    
    def generate() -> Generator:
        for data in chatBot.askStream(question):
            yield core.GenerateResponse().success({
                'answer': data.get('answer'),
                'urls': data.get('urls'),
                'done': data.get('done'),
                'token': token
            }, True)

    return StreamingResponse(generate(), media_type='text/event-stream')