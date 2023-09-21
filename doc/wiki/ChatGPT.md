## Ask
### 请求
1. 网址: /chatgpt/ask.
2. 方式: GET/POST.
3. 格式: JSON(当方式为POST时).
4. 参数:

名称|类型|必填|说明
---|---|---|---
question|String|是|
token|String|否|填则为连续对话,不填则为新对话,值可在响应中获取
### 响应
1. 格式: JSON.
2. 参数:

名称|类型|说明
---|---|---
code|Integer|
message|String|
data|Object|
answer|String|
spend|Integer|
token|String|用于连续对话
3. 示例:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "answer": "你好！很高兴能和你聊天。有什么我可以帮你的吗？",
        "spend": 71,
        "token": "d65b5b6a-bae3-4cfd-a8b1-07d15bb891c9"
    }
}
```
## Ask Stream
### 请求
1. 网址: /chatgpt/ask_stream.
2. 方式: GET/POST.
3. 格式: JSON(当方式为POST时).
4. 参数:

名称|类型|必填|说明
---|---|---|---
question|String|是|
token|String|否|填则为连续对话,不填则为新对话,值可在响应中获取
### 响应
1. 格式: Event-Stream.
2. 参数:

名称|类型|说明
---|---|---
code|Integer|
message|String|
data|Object|
answer|String|
spend|Integer|当done为true时,显示真实值
done|Bool|部分传输是否完成
token|String|用于连续对话
3. 示例:
```
data: {"code": 200, "message": "success", "data": {"answer": "你好！我是", "done": false, "spend": 0, "token": "84361cde-73fc-488b-b75f-c69d3602411d"}}

data: {"code": 200, "message": "success", "data": {"answer": "ChatGPT", "spend": 0, "done": false, "token": "84361cde-73fc-488b-b75f-c69d3602411d"}}

data: {"code": 200, "message": "success", "data": {"answer": "，", "spend": 0, "done": false, "token": "84361cde-73fc-488b-b75f-c69d3602411d"}}

data: {"code": 200, "message": "success", "data": {"answer": "你好！我是ChatGPT，很高兴能和你交流。有什么可以帮助你的吗？", "spend": 0, "done": false, "token": "84361cde-73fc-488b-b75f-c69d3602411d"}}

data: {"code": 200, "message": "success", "data": {"answer": "？", "spend": 0, "done": false, "token": "84361cde-73fc-488b-b75f-c69d3602411d"}}

data: {"code": 200, "message": "success", "data": {"answer": "你好！我是ChatGPT，很高兴能和你交流。有什么可以帮助你的吗？", "spend": 77, "done": True, "token": "84361cde-73fc-488b-b75f-c69d3602411d"}}
```