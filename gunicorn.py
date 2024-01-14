from config import HTTP

workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'

bind = f'{HTTP["host"]}:{HTTP["port"]}'
if HTTP['ssl']['enable']:
    keyfile = HTTP['ssl']['keyPath']
    certfile = HTTP['ssl']['certPath']