## 提示
1. 升级咯,此仓库前身为Bing-Chat,现已更名为Chat-API,支持多种Chat,现已支持ChatGPT,Bing Chat,Bard,文心一言.
2. 若报错,请先将ChatGPT,EdgeGPT,BingImageCreator,GoogleBard,easy-ernie更新到最新版本.
## 介绍
一款基于Python-FastAPI框架,开发的多种Chat接口程序.
## 需求
1. 语言: Python3.8+.
2. 包: fastapi,python-multipart,uvicorn,asyncio,EdgeGPT,BingImageCreator,GoogleBard,easy-ernie
3. 其他: New Bing账户,Bard账户.
## 配置(config.py)
1. 监听地址和端口分别在第4行和第5行.
2. Proxy在第6行.
3. ChatGPT密钥在第7行.
## Cookie(cookie/)
1. 浏览器安装Cookie-Editor扩展.
2. 访问[Bing Chat](https://www.bing.com/chat)/[Bard](https://bard.google.com)/[文心一言](https://yiyan.baidu.com).
3. 在页面中点击扩展.
4. 点击扩展右下角的Export-Export as JSON
5. 将复制的内容粘贴到对应的Cookie文件.
## 接口文档
查看[Wiki](https://github.com/XiaoXinYo/Chat-API/wiki).  
提示: 在使用Chat前,请确保对应的Cookie已配置好,ChatGPT密钥需要在config.py文件中写.
## emm
1. 搭建好建议不要对外开放，因为目前Bing Chat24小时内有次数限制.
2. 至于反应快慢的问题，要看回答文本的长度，如果文本长度过长，回复时间会比较长.
3. 关于整体传输和流传输，整体传输由于要等待完全响应才能开始传输，所以时间要久一点。流传输会先返回一部分，所以看起来比较快，但其实最终的完成时间都是一样的.
4. 如果需要进行连续对话，首先需要在第一次请求时获取token，然后在后续请求中带上token，就可以实现连续对话了.