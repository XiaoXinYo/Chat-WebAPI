from fastapi import APIRouter, Request, Response
from module import core, chat

BARD_APP = APIRouter()

@BARD_APP.route('/ask', methods=['GET', 'POST'])
async def ask(request: Request) -> Response:
    parameter = await core.getRequestParameter(request)
    question = parameter.get('question')
    token = parameter.get('token')
    if not question:
        return core.GenerateResponse().error(110, '参数不能为空')

    if token:
        chatG = chat.get(chat.Type.BARD, token)
        if not chatG:
            return core.GenerateResponse().error(110, 'token不存在')

        bot = chatG.bot
    else:
        token, bot = await chat.generate(chat.Type.BARD)

    data = bot.get_answer(question)
    urls = data['links']
    imageUrls = data['images']
    urls = [url for url in urls if url not in imageUrls]
    return core.GenerateResponse().success({
        'answer':  data['content'],
        'urls': urls,
        'imageUrls': imageUrls,
        'token': token
    })