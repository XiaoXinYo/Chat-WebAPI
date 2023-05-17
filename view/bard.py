# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from fastapi import APIRouter, Request, Response
from module import core, auxiliary, chat_bot
import json
import re

Bard_APP = APIRouter()

@Bard_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getrequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')
    elif not auxiliary.isEnglish(question):
        return core.GenerateResponse().error(110, 'question仅支持英文')

    if token:
        chatBot = chat_bot.getChatBot(token)
        if not chatBot:
            return core.GenerateResponse().error(120, 'token不存在')
        chatBot = chatBot['chatBot']
    else:
        token, chatBot = chat_bot.generateChatBot('Bard')

    data = chatBot.ask(question)
    answer = data['content']
    url = json.dumps(data['factualityQueries'])
    urls = re.findall(r'"(http.*?)"', url)
    
    return core.GenerateResponse().success({
        'answer': answer,
        'urls': urls,
        'token': token
    })