## Ask
### 请求
1. 网址: /bing/ask.
2. 方式: GET/POST.
3. 格式: JSON(当方式为POST时).
4. 参数:

名称|类型|必填|说明
---|---|---|---
question|String|是|
style|String|否|balanced代表平衡,creative代表创造,precise代表精确,默认为balanced
prompt|String|否|仅支持英文,sydney代表Sydney,可自定义
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
suggests|List|
urls|List|
reset|Bool|下次对话是否被重置(code为500时也会被重置)
token|String|用于连续对话
3. 示例:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "answer": "您好，这是必应。",
        "suggests": [
            "必应是什么？"
        ],
        "urls": [
            {
                "title": "The New Bing - Learn More",
                "url": "https://www.bing.com/new"
            }
        ],
        "reset": false,
        "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"
    }
}
```
## Ask Stream
### 请求
1. 网址: /bing/ask_stream.
2. 方式: GET/POST.
3. 格式: JSON(当方式为POST时).
4. 参数:

名称|类型|必填|说明
---|---|---|---
question|String|是|
style|String|否|balanced代表平衡,creative代表创造,precise代表精确,默认为balanced
prompt|String|否|仅支持英文,sydney代表Sydney,可自定义
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
suggests|List|当done为true时,显示真实值
urls|List|当done为true时,显示真实值
done|Bool|部分传输是否完成
reset|Bool|下次对话是否被重置(code为500时也会被重置),当done为true时,显示真实值
token|String|用于连续对话
3. 示例:
```
data: {"code": 200, "message": "success", "data": {"answer": "您。", "suggests": [], "urls": [], "done": false, "reset": false, "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"}}

data: {"code": 200, "message": "success", "data": {"answer": "好", "suggests": [], "urls": [], "done": false, "reset": false, "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"}}

data: {"code": 200, "message": "success", "data": {"answer": "，", "suggests": [], "urls": [], "done": false, "reset": false, "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"}}

data: {"code": 200, "message": "success", "data": {"answer": "这。", "suggests": [], "urls": [], "done": false, "reset": false, "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"}}

data: {"code": 200, "message": "success", "data": {"answer": "是", "suggests": [], "urls": [], "done": false, "reset": false, "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"}}

data: {"code": 200, "message": "success", "data": {"answer": "必应", "suggests": [], "urls": [], "done": false, "reset": false, "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"}}

data: {"code": 200, "message": "success", "data": {"answer": "。", "suggests": [], "urls": [], "done": false, "reset": false, "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"}}

data: {"code": 200, "message": "success", "data": {"answer": "您好，这是必应。", "suggests": ["什么是必应？"], "urls": [{"title": "The New Bing - Learn More", "url": "https://www.bing.com/new"}], "done": true, "reset": false, "token": "7953d67b-eac2-457e-a2ee-fedc8ba53599"}}
```
## 图像生成
### 请求
### 请求
1. 网址: /bing/image.
2. 方式: GET/POST.
3. 格式: JSON(当方式为POST时).
4. 参数:

名称|类型|必填|说明
---|---|---|---
keyword|String|是|
### 响应
1. 格式: JSON.
2. 参数:

名称|类型|说明
---|---|---
code|Integer|
message|String|
data|List|
3. 示例:
```json
{
    "code": 200,
    "message": "success",
    "data": [
        "https://tse2.mm.bing.net/th/id/OIG.gZ22nCCQkj48ydKsjZKa",
        "https://tse2.mm.bing.net/th/id/OIG.rAYVVytOqj.ajgCh2ZtZ",
        "https://tse3.mm.bing.net/th/id/OIG.X8tmgTvvlIwtvSiFyHSE",
        "https://tse2.mm.bing.net/th/id/OIG.10fmeQUY9GO.wNV5FjzI"
    ]
}
```