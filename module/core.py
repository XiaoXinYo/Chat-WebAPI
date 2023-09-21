from typing import Union, Any
from fastapi import Request, Response
import json

async def getRequestParameter(request: Request) -> dict:
    data = {}
    if request.method == 'GET':
        data = request.query_params
    elif request.method == 'POST':
        data = await request.json()
    return dict(data)

class GenerateResponse:
    TYPE = Union[str, Response]

    def __init__(self):
        self.code = 0
        self.message = ''
        self.data = None
        self.httpCode = 200
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
        return Response(responseJSON, status_code=self.httpCode, media_type='application/json')

    def error(self, code: int, message: str, streamFormat=False, streamResponse=False, httpCode=200) -> TYPE:
        self.code = code
        self.message = message
        self.streamFormat = streamFormat
        self.streamResponse = streamResponse
        self.httpCode = httpCode
        return self.generate()

    def success(self, data: Any, streamFormat=False) -> TYPE:
        self.code = 200
        self.message = 'success'
        self.data = data
        self.streamFormat = streamFormat
        return self.generate()