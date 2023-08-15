from typing import Generator
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
from module import core, chat_bot

ERNIE_APP = APIRouter()

@ERNIE_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')

    if token:
        chatBot = chat_bot.getChatBot(token)
        if not chatBot:
            return core.GenerateResponse().error(120, 'token不存在')
    else:
        token, chatBot = chat_bot.generateChatBot('Ernie')

    data = chatBot.ask(question)
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
        chatBot = chat_bot.getChatBot(token)
        if not chatBot:
            return core.GenerateResponse().error(120, 'token不存在', streamResponse=True)
    else:
        token, chatBot = chat_bot.generateChatBot('Ernie')
    
    def generate() -> Generator:
        for data in chatBot.askStream(question):
            yield core.GenerateResponse().success({
                'answer': data['answer'],
                'urls': data['urls'],
                'done': data['done'],
                'token': token
            }, True)
    return StreamingResponse(generate(), media_type='text/event-stream')