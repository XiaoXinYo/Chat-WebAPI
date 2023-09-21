from fastapi import APIRouter, Request, Response
from module import core, auxiliary, chat_bot
import json
import re

Bard_APP = APIRouter()

@Bard_APP.route('/ask', methods=['GET', 'POST'])
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
        token, chatBot = chat_bot.generateChatBot('Bard')

    data = chatBot.ask(question)
    url = json.dumps(data['factualityQueries'])
    urls = re.findall(r'"(http.*?)"', url)
    return core.GenerateResponse().success({
        'answer':  data['content'],
        'urls': urls,
        'imageUrls': data['images'],
        'token': token
    })