from typing import Generator
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
from module import core, chat_bot

CHATGPT_APP = APIRouter()

@CHATGPT_APP.route('/ask', methods=['GET', 'POST'])
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
        token, chatBot = chat_bot.generateChatBot('ChatGPT')

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
        token, chatBot = chat_bot.generateChatBot('ChatGPT')
    
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
            yield core.GenerateResponse().error(500, '未知错误', streamFormat=True)
    return StreamingResponse(generate(), media_type='text/event-stream')