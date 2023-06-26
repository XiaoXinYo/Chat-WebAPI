# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from config import HOST, PORT, SSL

workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'

bind = f'{HOST}:{PORT}'
if SSL['enable']:
    keyfile = SSL['keyPath']
    certfile = SSL['certPath']