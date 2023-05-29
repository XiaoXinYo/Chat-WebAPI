# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from typing import Union, Any
from fastapi import Request, Response
import json

async def getrequestParameter(request: Request) -> dict:
    data = {}
    if request.method == 'GET':
        data = request.query_params
    elif request.method == 'POST':
        data = await request.form()
        if not data:
            data = await request.json()
    return dict(data)

class GenerateResponse:
    TYPE = Union[str, Response]

    def __init__(self):
        self.code = 0
        self.message = ''
        self.data = None
        self.streamFormat = False
        self.streamResponse = False

    def generate(self) -> TYPE:
        responseJSON = json.dumps({
            'code': self.code,
            'message': self.message,
            'data': self.data
        }, ensure_ascii=False)
        if self.streamFormat:
            return f'data: {responseJSON}\n\n'
        if self.streamResponse:
            return Response(f'data: {responseJSON}\n\n', media_type='text/event-stream')
        return Response(responseJSON, media_type='application/json')

    def error(self, code: int, message: str, streamFormat=False, streamResponse=False) -> TYPE:
        self.code = code
        self.message = message
        self.streamFormat = streamFormat
        self.streamResponse = streamResponse
        return self.generate()

    def success(self, data: Any, streamFormat=False) -> TYPE:
        self.code = 200
        self.message = 'success'
        self.data = data
        self.streamFormat = streamFormat
        return self.generate()