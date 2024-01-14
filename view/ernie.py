from typing import Generator
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
from module import core, chat

ERNIE_APP = APIRouter()

@ERNIE_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')

    if token:
        chatG = chat.get(chat.Type.ERNIE, token)
        if not chatG:
            return core.GenerateResponse().error(110, 'token不存在')

        bot = chatG.bot
    else:
        token, bot = await chat.generate(chat.Type.ERNIE)

    data = bot.ask(question)
    return core.GenerateResponse().success({
        'answer': data['answer'],
        'urls': data['urls'],
        'token': token
    })

@ERNIE_APP.route('/ask_stream', methods=['GET', 'POST'])
async def askStream(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空', streamResponse=True)
    
    if token:
        chatG = chat.get(chat.Type.ERNIE, token)
        if not chatG:
            return core.GenerateResponse().error(110, 'token不存在', streamResponse=True)

        bot = chatG.bot
    else:
        token, bot = await chat.generate(chat.Type.ERNIE)
    
    async def generate() -> Generator:
        for data in bot.askStream(question):
            yield core.GenerateResponse().success({
                'answer': data['answer'],
                'urls': data['urls'],
                'done': data['done'],
                'token': token
            }, streamFormat=True)
    return StreamingResponse(generate(), media_type='text/event-stream')