from typing import Optional, Generator
import requests
import json

MODELS = [
    'gpt-3.5-turbo',
    'gpt-4'
]

class ChatGPT:
    def __init__(self, apiKey: str, apiUrl: str='https://api.openai.com', proxy: Optional[dict]=None) -> None:
        self.apiUrl = apiUrl
        self.apiKey = apiKey
        self.messages = []
        self.session = requests.Session()
        self.session.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {apiKey}'
        }
        if proxy:
            self.session.proxies = proxy

    def checkJson(self, data: str) -> None:
        try:
            print(data)
            data = json.loads(data)
        except:
            raise Exception('请求失败,响应格式错误')

        if 'error' in data:
            raise Exception(f'请求失败,{data["error"]["message"]}')

    def request(self, method: str, url: str, data: Optional[dict] = None, stream=False,
                check=True) -> requests.Response:
        if method == 'get':
            self.response = self.session.get(url, params=data, stream=stream)
        else:
            self.session.headers['Content-Length'] = str(len(data))
            self.response = self.session.request(method, url, data=json.dumps(data), stream=stream)

        if not stream and check:
            self.checkJson(self.response.text)
        return self.response

    def get(self, url: str, data: Optional[dict] = None, stream=False, check=True) -> requests.Response:
        return self.request('get', url, data, stream=stream, check=check)

    def post(self, url: str, data: dict, stream=False, check=True) -> requests.Response:
        return self.request('post', url, data, stream=stream, check=check)

    @staticmethod
    def getModel() -> list:
        return MODELS

    def askStream(self, model: str, question: str) -> Generator:
        if model not in MODELS:
            raise Exception(f'{model}模型不存在')

        self.messages.append({
            'role': 'user',
            'content': question
        })
        response = self.post(
            f'{self.apiUrl}/v1/chat/completions',
            {
                'model': model,
                'messages': self.messages,
                'stream': True,
            },
            stream=True,
            check=False
        )
        if response.headers.get('Content-Type') != 'text/event-stream':
            self.checkJson(response.text)

        fullAnswer = ''
        for line in response.iter_lines():
            if not line:
                continue

            line = line.decode('utf-8')
            data = line[6:]
            data = json.loads(data)
            choices = data['choices'][0]
            if answer := choices['delta'].get('content'):
                fullAnswer += answer
                yield {
                    'answer': answer,
                    'done': False
                }
            elif choices['finish_reason'] == 'stop':
                yield {
                    'answer': fullAnswer,
                    'done': True
                }
                break

        self.messages.append({
            'role': 'system',
            'content': fullAnswer
        })

    def ask(self, model: str, question: str) -> str:
        for data in self.askStream(model, question):
            if data['done']:
                return data['answer']