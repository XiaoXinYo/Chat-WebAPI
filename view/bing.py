from typing import AsyncGenerator
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
from module import core, chat
import re_edge_gpt
import re

BING_APP = APIRouter()
STYLES = ['balanced', 'creative', 'precise']

def getStyleEnum(style: str) -> re_edge_gpt.ConversationStyle:
    enum = re_edge_gpt.ConversationStyle
    if style == 'balanced':
        enum = enum.balanced
    elif style == 'creative':
        enum = enum.creative
    elif style == 'precise':
        enum = enum.precise
    return enum

def todayUpperLimit(data: dict) -> bool:
    return data['item']['result']['value'] == 'Throttled'

def filterAnswer(answer: str) -> str:
    answer = answer.replace('- **', '').replace('**', '')
    answer = re.sub('\[\^.*?\^]', '', answer)
    return answer

def getAnswer(data: dict) -> str:
    messages = data['item']['messages']
    for message in messages:
        if 'suggestedResponses' not in message:
            continue
        return filterAnswer(message['text'])
    return ''

def getUrl(data: dict) -> list:
    messages = data['item']['messages']
    urls = []
    for message in messages:
        sourceAttributions = message.get('sourceAttributions')
        if not sourceAttributions:
            continue
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
    return False

@BING_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    style = parameter.get('style', 'balanced')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    elif style not in STYLES:
        return core.GenerateResponse().error(110, 'style不存在')

    if token:
        chatG = chat.get(chat.Type.BING, token)
        if not chatG:
            return core.GenerateResponse().error(110, 'token不存在')

        bot = chatG.bot
    else:
        token, bot = await chat.generate(chat.Type.BING)

    data = await bot.ask(question, conversation_style=getStyleEnum(style))
    if todayUpperLimit(data):
        return core.GenerateResponse().error(130, '已上限,24小时后尝试')

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
        await bot.reset()
        info['reset'] = True

    return core.GenerateResponse().success(info)


@BING_APP.route('/ask_stream', methods=['GET', 'POST'])
async def askStream(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    style = parameter.get('style', 'balanced')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空', streamResponse=True)
    elif style not in STYLES:
        return core.GenerateResponse().error(110, 'style不存在', streamResponse=True)

    if token:
        chatG = chat.get(chat.Type.BING, token)
        if not chatG:
            return core.GenerateResponse().error(110, 'token不存在')

        bot = chatG.bot
    else:
        token, bot = await chat.generate(chat.Type.BING)

    async def generator() -> AsyncGenerator:
        index = 0
        info = {
            'answer': '',
            'urls': [],
            'done': False,
            'reset': False,
            'token': token
        }
        async for final, data in bot.ask_stream(question, conversation_style=getStyleEnum(style), raw=True):
            if not final:
                if 'sourceAttributions' not in data['arguments'][0].get('messages', [{}])[0]:
                    continue

                text = data['arguments'][0]['messages'][0]['text']
                answer = text[index:]
                index = len(text)
                answer = filterAnswer(answer)
                if answer:
                    info['answer'] = answer
                    yield core.GenerateResponse().success(info, streamFormat=True)
            else:
                if todayUpperLimit(data):
                    yield core.GenerateResponse().error(120, '已上限,24小时后尝试', streamFormat=True)
                    break

                answer = getAnswer(data)
                info['answer'] = answer
                info['urls'] = getUrl(data)
                info['done'] = True

                if needReset(data, answer):
                    await bot.reset()
                    info['reset'] = True

                yield core.GenerateResponse().success(info, streamFormat=True)
    return StreamingResponse(generator(), media_type='text/event-stream')