# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from typing import AsyncGenerator
from fastapi import APIRouter, Request, Response
from module import auxiliary, core
import asyncio
import config
import uuid
from EdgeGPT import Chatbot, ConversationStyle
import re
import BingImageCreator
from fastapi.responses import StreamingResponse

BingAPP = APIRouter()
STYLES = ['balanced', 'creative', 'precise']
CHATBOT = {}

async def checkToken():
    global CHATBOT
    while True:
        for token in CHATBOT.copy():
            chatBot = CHATBOT[token]
            if auxiliary.getTimeStamp() - chatBot.get('useTimeStamp') > 5 * 60:
                await chatBot.get('chatBot').close()
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
        chatBot = Chatbot(proxy=config.PROXY, cookie_path='./cookie/bing.json')
        token = str(uuid.uuid4())
        CHATBOT[token] = {}
        CHATBOT[token]['chatBot'] = chatBot
    CHATBOT[token]['useTimeStamp'] = auxiliary.getTimeStamp()
    return token, chatBot

def getStyleEnum(style: str) -> ConversationStyle:
    enum = ConversationStyle
    if style == 'balanced':
        enum = enum.balanced
    elif style == 'creative':
        enum = enum.creative
    elif style == 'precise':
        enum = enum.precise
    return enum

def filterAnswer(answer: str) -> str:
    answer = re.sub(r'\[\^.*?\^]', '', answer)
    return answer

def getAnswer(data: dict) -> str:
    messages = data.get('item').get('messages')
    if 'text' in messages[1]:
        return filterAnswer(messages[1].get('text'))
    else:
        return filterAnswer(messages[1].get('adaptiveCards')[0].get('body')[0].get('text'))

def getStreamAnswer(data: dict) -> str:
    messages = data.get('item').get('messages')
    if 'text' in messages[1]:
        answer = messages[1].get('text')
    else:
        answer = messages[1].get('adaptiveCards')[0].get('body')[0].get('text')
    answer = filterAnswer(answer)
    return answer

def getUrl(data: dict) -> list:
    sourceAttributions = data.get('item').get('messages')[1].get('sourceAttributions')
    urls = []
    if sourceAttributions:
        for sourceAttribution in sourceAttributions:
            urls.append({
                'title': sourceAttribution.get('providerDisplayName'),
                'url': sourceAttribution.get('seeMoreUrl')
            })
    return urls

def needReset(data: dict, answer: str) -> bool:
    maxTimes = data.get('item').get('throttling').get('maxNumUserMessagesInConversation')
    nowTimes = data.get('item').get('throttling').get('numUserMessagesInConversation')
    errorAnswers = ['I’m still learning', '我还在学习']
    if [errorAnswer for errorAnswer in errorAnswers if errorAnswer in answer]:
        return True
    elif nowTimes == maxTimes:
        return True
    return False

@BingAPP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    style = parameter.get('style')
    question = parameter.get('question')
    token = parameter.get('token')
    if not style or not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    elif style not in STYLES:
        return core.GenerateResponse().error(110, 'style不存在')
    
    token, chatBot = getChatBot(token)
    if not chatBot:
        return core.GenerateResponse().error(120, 'token不存在')
    data = await chatBot.ask(question, conversation_style=getStyleEnum(style))

    if data.get('item').get('result').get('value') == 'Throttled':
        return core.GenerateResponse().error(120, '已上限,24小时后尝试')

    info = {
        'answer': '',
        'urls': [],
        'reset': False,
        'token': token
    }
    answer = getAnswer(data)
    answer = filterAnswer(answer)
    info['answer'] = answer
    info['urls'] = getUrl(data)
    
    if needReset(data, answer):
        await chatBot.reset()
        info['reset'] = True
    
    return core.GenerateResponse().success(info)

@BingAPP.route('/ask_stream', methods=['GET', 'POST'])
async def askStream(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    style = parameter.get('style')
    question = parameter.get('question')
    token = parameter.get('token')
    if not style or not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    elif style not in STYLES:
        return core.GenerateResponse().error(110, 'style不存在')
    
    token, chatBot = getChatBot(token)
    if not chatBot:
        return core.GenerateResponse().error(120, 'token不存在')
    
    async def generator() -> AsyncGenerator:
        index = 0
        info = {
            'answer': '',
            'urls': [],
            'done': False,
            'reset': False,
            'token': token
        }
        async for final, data in chatBot.ask_stream(question, conversation_style=getStyleEnum(style)):
            if not final:
                answer = data[index:]
                index = len(data)
                answer = filterAnswer(answer)
                if answer:
                    info['answer'] = answer
                    yield core.GenerateResponse().success(info, True)
            else:
                if data.get('item').get('result').get('value') == 'Throttled':
                    yield core.GenerateResponse().error(120, '已上限,24小时后尝试', True)
                    break
                
                messages = data.get('item').get('messages')
                info['answer'] = getStreamAnswer(data)
                if 'text' not in messages[1]:
                    yield core.GenerateResponse().success(info, True)
                info['done'] = True
                info['urls'] = getUrl(data)

                if needReset(data, answer):
                    await chatBot.reset()
                    info['reset'] = True
                
                yield core.GenerateResponse().success(info, True)
    
    return StreamingResponse(generator(), media_type='text/event-stream')

@BingAPP.route('/image', methods=['GET', 'POST'])
async def image(request: Request) -> Response:
    keyword = (await core.getrequestParameter(request)).get('keyword')
    if not keyword:
        return core.GenerateResponse().error(110, '参数不能为空')
    elif not auxiliary.isEnglish(keyword):
        return core.GenerateResponse().error(110, '仅支持英文')
    
    cookie = auxiliary.getCookie('./cookie/bing.json', ['_U']).get('_U')
    return core.GenerateResponse().success(BingImageCreator.ImageGen(cookie).get_images(keyword))