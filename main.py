from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from view import bard, bing, chatgpt, claude, ernie
from module import chat, core
import asyncio
import config
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(chat.check())
    yield
    await chat.check(loop=False)

APP = FastAPI(lifespan=lifespan)
APP.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
APP.include_router(bard.BARD_APP, prefix='/bard')
APP.include_router(bing.BING_APP, prefix='/bing')
APP.include_router(chatgpt.CHATGPT_APP, prefix='/chatgpt')
APP.include_router(claude.CLAUDE_APP, prefix='/claude')
APP.include_router(ernie.ERNIE_APP, prefix='/ernie')

@APP.middleware('http')
async def middleware(request: Request, call_next) -> None:
    urls = request.url.path.split('/')
    if len(urls) == 3:
        model = urls[1]
        mode = urls[2]
        if mode == 'ask':
            generate = lambda model: core.GenerateResponse().error(100, f'{model}未配置')
        else:
            generate = lambda model: core.GenerateResponse().error(100, f'{model}未配置', streamResponse=True)
        if model == 'bard':
            if not chat.BARD_COOKIE:
                return generate('Bard')
        elif model == 'bing':
            if not chat.BING_COOKIE:
                return generate('Bing')
        elif model == 'chatgpt':
            if not config.CHATGPT_KEY:
                return generate('ChatGPT')
        elif model == 'claude':
            if not chat.CLAUDE_COOKIE:
                return generate('Claude')
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
        'host': config.HTTP['host'],
        'port': config.HTTP['port']
    }
    if config.HTTP['ssl']['enable']:
        uvicorn.run(APP, **appConfig, ssl_keyfile=config.HTTP['ssl']['keyPath'], ssl_certfile=config.HTTP['ssl']['certPath'])
    else:
        uvicorn.run(APP, **appConfig)