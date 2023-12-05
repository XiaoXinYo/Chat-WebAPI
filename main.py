from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from view import bard, chatgpt, ernie
from module import chat, core
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
APP.include_router(bard.Bard_APP, prefix='/bard')
APP.include_router(chatgpt.CHATGPT_APP, prefix='/chatgpt')
APP.include_router(ernie.ERNIE_APP, prefix='/ernie')

@APP.on_event('startup')
async def startup() -> None:
    asyncio.create_task(chat.check())

@APP.on_event('shutdown')
async def shutdown() -> None:
    asyncio.create_task(chat.check(loop=False))

@APP.middleware('http')
async def middleware(request: Request, call_next) -> None:
    urls = request.url.path.split('/')
    if len(urls) == 3:
        model = urls[1]
        mode = urls[2]
        if mode == 'ask':
            generate = lambda model_: core.GenerateResponse().error(100, f'{model_}未配置')
        else:
            generate = lambda model_: core.GenerateResponse().error(100, f'{model_}未配置', streamResponse=True)
        if model == 'bard':
            if not chat.BARD_COOKIE:
                return generate('Bard')
        elif model == 'chatgpt':
            if not config.CHATGPT_KEY:
                return generate('ChatGPT')
        elif model == 'ernie':
            if not chat.ERNIE_COOKIE:
                return generate('文心一言')

    response = await call_next(request)
    return response

@APP.exception_handler(404)
def error404(request: Request, exc: Exception) -> Response:
    return core.GenerateResponse().error(404, '未找到文件', httpCode=404)

@APP.exception_handler(500)
def error500(request: Request, exc: Exception) -> Response:
    return core.GenerateResponse().error(500, '未知错误', httpCode=500)

if __name__ == '__main__':
    appConfig = {
        'host': config.HOST,
        'port': config.PORT,
    }
    if config.SSL['enable']:
        uvicorn.run(APP, **appConfig, ssl_keyfile=config.SSL['keyPath'], ssl_certfile=config.SSL['certPath'])
    else:
        uvicorn.run(APP, **appConfig)