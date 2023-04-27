# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from typing import Generator
from fastapi import APIRouter, Request, Response
from module import core, auxiliary
import asyncio
import config
from revChatGPT.V3 import Chatbot
import uuid
from fastapi.responses import StreamingResponse

CHATGPT_APP = APIRouter()
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
        chatBot = Chatbot(config.CHATGPT_KEY)
        token = str(uuid.uuid4())
        CHATBOT[token] = {}
        CHATBOT[token]['chatBot'] = chatBot
        CHATBOT[token]['useTimeStamp'] = auxiliary.getTimeStamp()
    return token, chatBot

@CHATGPT_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    
    token, chatBot = getChatBot(token)
    if not chatBot:
        return core.GenerateResponse().error(120, 'token不存在')

    try:
        return core.GenerateResponse().success({
            'answer': chatBot.ask(question),
            'spend': chatBot.get_token_count(),
            'token': token
        })
    except:
        return core.GenerateResponse().error(500, '未知错误')

@CHATGPT_APP.route('/ask_stream', methods=['GET', 'POST'])
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
        fullAnswer = ''
        try:
            for answer in chatBot.ask_stream(question):
                fullAnswer += answer
                yield core.GenerateResponse().success({
                    'answer': answer,
                    'spend': 0,
                    'done': False,
                    'token': token
                }, True)
            yield core.GenerateResponse().success({
                'answer': fullAnswer,
                'spend': chatBot.get_token_count(),
                'done': True,
                'token': token
            }, True)
        except:
            yield core.GenerateResponse().error(500, '未知错误', True)

    return StreamingResponse(generate(), media_type='text/event-stream')