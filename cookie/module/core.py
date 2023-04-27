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
        self.response = {}
        self.onlyJSON = False
    
    def json(self) -> TYPE:
        responseJSON = json.dumps(self.response, ensure_ascii=False)
        if self.stream:
            return f'data: {responseJSON}\n\n'
        return Response(responseJSON, media_type='application/json')

    def error(self, code: int, message: str, stream=False) -> TYPE:
        self.response = {
            'code': code,
            'message': message,
            'data': None
        }
        self.stream = stream
        return self.json()

    def success(self, data: Any, stream=False) -> TYPE:
        self.response = {
            'code': 200,
            'message': 'success',
            'data': data
        }
        self.stream = stream
        return self.json()