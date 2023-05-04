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
            if auxiliary.getTimeStamp() - chatBot['useTimeStamp'] > 5 * 60:
                await chatBot['chatBot'].close()
                del chatBot
        await asyncio.sleep(60)

def getChatBot(token: str) -> tuple:
    global CHATBOT
    if token:
        if token in CHATBOT:
            chatBot = CHATBOT[token]['chatBot']
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
    messages = data['item']['messages']
    for message in messages:
        if 'suggestedResponses' in message:
            if 'text' in message:
                return filterAnswer(message['text'])
            return filterAnswer(message['adaptiveCards'][0]['body'][0]['text'])

def getSuggest(data: dict) -> list:
    messages = data['item']['messages']
    suggests = []
    for message in messages:
        suggestedResponses = message.get('suggestedResponses')
        if suggestedResponses:
            for suggestedResponse in suggestedResponses:
                suggests.append(suggestedResponse['text'])
    return suggests

def getUrl(data: dict) -> list:
    messages = data['item']['messages']
    urls = []
    for message in messages:
        sourceAttributions = message.get('sourceAttributions')
        if sourceAttributions:
            for sourceAttribution in sourceAttributions:
                urls.append({
                    'title': sourceAttribution['providerDisplayName'],
                    'url': sourceAttribution['seeMoreUrl']
                })
    return urls

def needReset(data: dict, answer: str) -> bool:
    maxTimes = data['item']['throttling']['maxNumUserMessagesInConversation']
    nowTimes = data['item']['throttling']['numUserMessagesInConversation']
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

    if data['item']['result']['value'] == 'Throttled':
        return core.GenerateResponse().error(120, '已上限,24小时后尝试')

    info = {
        'answer': '',
        'suggests': [],
        'urls': [],
        'reset': False,
        'token': token
    }
    answer = getAnswer(data)
    answer = filterAnswer(answer)
    info['answer'] = answer
    info['suggests'] = getSuggest(data)
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
            'suggests': [],
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
                if data['item']['result']['value'] == 'Throttled':
                    yield core.GenerateResponse().error(120, '已上限,24小时后尝试', True)
                    break
                
                info['answer'] = getAnswer(data)
                info['suggests'] = getSuggest(data)
                info['urls'] = getUrl(data)
                info['done'] = True

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
    
    cookie = auxiliary.getCookie('./cookie/bing.json', ['_U'])['_U']
    return core.GenerateResponse().success(BingImageCreator.ImageGen(cookie).get_images(keyword))