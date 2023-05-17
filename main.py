# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from view import chatgpt, bing, bard, ernie
from module import chat_bot, core
import asyncio
import config
import uvicorn

APP = FastAPI()
APP.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
APP.include_router(chatgpt.CHATGPT_APP, prefix='/chatgpt')
APP.include_router(bing.BING_APP, prefix='/bing')
APP.include_router(bard.Bard_APP, prefix='/bard')
APP.include_router(ernie.ERNIE_APP, prefix='/ernie')

@APP.on_event('startup')
async def startup() -> None:
    asyncio.get_event_loop().create_task(chat_bot.checkChatBot())

@APP.exception_handler(404)
def error404(request: Request, exc: Exception) -> Response:
    return core.GenerateResponse().error(404, '未找到文件')

@APP.exception_handler(500)
def error500(request: Request, exc: Exception) -> Response:
    return core.GenerateResponse().error(500, '未知错误')

if __name__ == '__main__':
    uvicorn.run(APP, host=config.HOST, port=config.PORT)