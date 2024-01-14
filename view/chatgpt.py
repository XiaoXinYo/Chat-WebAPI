from typing import Generator
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
from module import core, chat, chatgpt

CHATGPT_APP = APIRouter()

@CHATGPT_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    model = parameter.get('model')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')

    if token:
        chatG = chat.get(chat.Type.CHATGPT, token)
        if not chatG:
            return core.GenerateResponse().error(110, 'token不存在')

        bot = chatG.bot
        modelG = chatG.parameter.get('model')
        if model:
            if model not in chatgpt.ChatGPT.getModel():
                return core.GenerateResponse().error(110, 'model不存在')
            elif model != modelG:
                chat.update(token, {'model': model})
        else:
            model = modelG
    else:
        if not model:
            return core.GenerateResponse().error(110, '参数不能为空')
        elif model not in chatgpt.ChatGPT.getModel():
            return core.GenerateResponse().error(110, 'model不存在')
        token, bot = await chat.generate(chat.Type.CHATGPT, {'model': model})

    return core.GenerateResponse().success({
        'answer': bot.ask(model, question),
        'token': token
    })

@CHATGPT_APP.route('/ask_stream', methods=['GET', 'POST'])
async def askStream(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    model = parameter.get('model')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空', streamResponse=True)

    if token:
        chatG = chat.get(chat.Type.CHATGPT, token)
        if not chatG:
            return core.GenerateResponse().error(110, 'token不存在')

        bot = chatG.bot
        modelG = chatG.parameter.get('model')
        if model:
            if model not in chatgpt.ChatGPT.getModel():
                return core.GenerateResponse().error(110, 'model不存在')
            elif model != modelG:
                chat.update(token, {'model': model})
        else:
            model = modelG
    else:
        if not model:
            return core.GenerateResponse().error(110, '参数不能为空')
        elif model not in chatgpt.ChatGPT.getModel():
            return core.GenerateResponse().error(110, 'model不存在')
        token, bot = await chat.generate(chat.Type.CHATGPT, {'model': model})
    
    def generate() -> Generator:
        for data in bot.askStream(model, question):
            if data['done']:
                yield core.GenerateResponse().success({
                    'answer': data['answer'],
                    'done': True,
                    'token': token
                }, streamFormat=True)
                break
            else:
                yield core.GenerateResponse().success({
                    'answer': data['answer'],
                    'done': False,
                    'token': token
                }, streamFormat=True)
    return StreamingResponse(generate(), media_type='text/event-stream')