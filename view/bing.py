# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from typing import Union, AsyncGenerator
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
from module import auxiliary, core, chat_bot
from EdgeGPT.conversation_style import ConversationStyle
import config
import re
import BingImageCreator

BING_APP = APIRouter()
STYLES = ['balanced', 'creative', 'precise']
IMAGE_COOKIE = auxiliary.getCookie('./cookie/bing.json', ['_U'])['_U']

def getStyleEnum(style: str) -> ConversationStyle:
    enum = ConversationStyle
    if style == 'balanced':
        enum = enum.balanced
    elif style == 'creative':
        enum = enum.creative
    elif style == 'precise':
        enum = enum.precise
    return enum

def getPrompt(prompt: Union[str, None]) -> Union[str, None]:
    if prompt:
        return f'[system](#additional_instructions)\n{config.BING_PROMPT.get(prompt, prompt)}'
    return None

def filterAnswer(answer: str) -> str:
    answer = re.sub(r'\[\^.*?\^]', '', answer)
    return answer

def getAnswer(data: dict) -> str:
    messages = data['item']['messages']
    for message in messages:
        if 'sourceAttributions' in message:
            if 'text' in message:
                return filterAnswer(message['text'])
            return filterAnswer(message['adaptiveCards'][0]['body'][0]['text'])
    return ''

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
    errorAnswers = ['I’m still learning', '我还在学习']
    maxTimes = data['item']['throttling']['maxNumUserMessagesInConversation']
    nowTimes = data['item']['throttling']['numUserMessagesInConversation']
    if [errorAnswer for errorAnswer in errorAnswers if errorAnswer in answer]:
        return True
    elif nowTimes == maxTimes:
        return True
    messages = data['item']['messages']
    for message in messages:
        if message.get('hiddenText') == '> Conversation disengaged':
            return True
    return False

@BING_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    question = parameter.get('question')
    style = parameter.get('style') or 'balanced'
    prompt = parameter.get('prompt') or ''
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    elif style not in STYLES:
        return core.GenerateResponse().error(110, 'style不存在')
    elif prompt and not auxiliary.isEnglish(prompt):
        return core.GenerateResponse().error(110, 'prompt仅支持英文')

    if token:
        chatBot = chat_bot.getChatBot(token)
        if not chatBot:
            return core.GenerateResponse().error(120, 'token不存在')
    else:
        token, chatBot = chat_bot.generateChatBot('Bing')

    data = await chatBot.ask(question, conversation_style=getStyleEnum(style), webpage_context=getPrompt(prompt))
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

@BING_APP.route('/ask_stream', methods=['GET', 'POST'])
async def askStream(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    question = parameter.get('question')
    style = parameter.get('style') or 'balanced'
    prompt = parameter.get('prompt') or ''
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空', streamResponse=True)
    elif style not in STYLES:
        return core.GenerateResponse().error(110, 'style不存在', streamResponse=True)
    elif prompt and not auxiliary.isEnglish(prompt):
        return core.GenerateResponse().error(110, 'prompt仅支持英文', streamResponse=True)

    if token:
        chatBot = chat_bot.getChatBot(token)
        if not chatBot:
            return core.GenerateResponse().error(120, 'token不存在', streamResponse=True)
    else:
        token, chatBot = chat_bot.generateChatBot('Bing')
    
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
        async for final, data in chatBot.ask_stream(question, conversation_style=getStyleEnum(style), webpage_context=getPrompt(prompt)):
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

                answer = getAnswer(data)
                info['answer'] = answer
                info['suggests'] = getSuggest(data)
                info['urls'] = getUrl(data)
                info['done'] = True

                if needReset(data, answer):
                    await chatBot.reset()
                    info['reset'] = True
                
                yield core.GenerateResponse().success(info, True)
    
    return StreamingResponse(generator(), media_type='text/event-stream')

@BING_APP.route('/image', methods=['GET', 'POST'])
async def image(request: Request) -> Response:
    keyword = (await core.getrequestParameter(request)).get('keyword')
    if not keyword:
        return core.GenerateResponse().error(110, '参数不能为空')
    elif not auxiliary.isEnglish(keyword):
        return core.GenerateResponse().error(110, 'keyword仅支持英文')

    return core.GenerateResponse().success(BingImageCreator.ImageGen(IMAGE_COOKIE, all_cookies=chat_bot.BING_COOKIE).get_images(keyword))