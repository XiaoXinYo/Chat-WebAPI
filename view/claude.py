from fastapi import APIRouter, Request, Response
from module import core, chat

CLAUDE_APP = APIRouter()

@CLAUDE_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')

    if token:
        chatG = chat.get(chat.Type.CLAUDE, token)
        if not chatG:
            return core.GenerateResponse().error(110, 'token不存在')

        bot = chatG.bot
        chatId = chatG.parameter['chatId']
    else:
        token, bot = await chat.generate(chat.Type.CLAUDE)
        chatId = chat.get(chat.Type.CLAUDE, token).parameter['chatId']

    data = bot.send_message(chatId, question)
    return core.GenerateResponse().success({
        'answer':  data.answer,
        'token': token
    })