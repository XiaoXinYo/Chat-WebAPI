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
        chat_ = chat.get(token)
        if not chat_:
            return core.GenerateResponse().error(120, 'token不存在')
        bot = chat_.bot
        model_ = chat_.parameter.get('model')
        if model:
            if model not in chatgpt.ChatGPT.getModel():
                return core.GenerateResponse().error(110, 'model不存在')
            if model != model_:
                chat.update(token, {'model': model})
        else:
            model = model_
    else:
        if not model:
            return core.GenerateResponse().error(110, '参数不能为空')
        elif model not in chatgpt.ChatGPT.getModel():
            return core.GenerateResponse().error(110, 'model不存在')
        token, bot = chat.generate(chat.Type.CHATGPT, {'model': model})

    try:
        return core.GenerateResponse().success({
            'answer': bot.ask(model, question),
            'token': token
        })
    except:
        return core.GenerateResponse().error(500, '未知错误')

@CHATGPT_APP.route('/ask_stream', methods=['GET', 'POST'])
async def askStream(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    model = parameter.get('model')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空', streamResponse=True)

    if token:
        chat_ = chat.get(token)
        if not chat_:
            return core.GenerateResponse().error(120, 'token不存在')
        bot = chat_.bot
        model_ = chat_.parameter.get('model')
        if model:
            if model not in chatgpt.ChatGPT.getModel():
                return core.GenerateResponse().error(110, 'model不存在')
            if model != model_:
                chat.update(token, {'model': model})
        else:
            model = model_
    else:
        if not model:
            return core.GenerateResponse().error(110, '参数不能为空')
        elif model not in chatgpt.ChatGPT.getModel():
            return core.GenerateResponse().error(110, 'model不存在')
        token, bot = chat.generate(chat.Type.CHATGPT, {'model': model})
    
    def generate() -> Generator:
        try:
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
        except:
            yield core.GenerateResponse().error(500, '未知错误', streamFormat=True)
    return StreamingResponse(generate(), media_type='text/event-stream')