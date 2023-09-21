## Ask
### 请求
1. 网址: /bard/ask.
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
urls|List|
images|List|
token|String|用于连续对话
3. 示例:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "answer": "Hello! How can I help you today?",
        "urls": [
            "https:bard.google.com(Bard)"
        ],
        "images": [
            "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png"
        ],
        "token": "8953d67b-eac2-457e-a2ee-fedc8ba53599"
    }
}
```