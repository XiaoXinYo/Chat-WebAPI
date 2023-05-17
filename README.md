## 提示
1. 升级咯,此仓库前身为Bing-Chat,现已更名为Chat-API,支持多种Chat,现已支持ChatGPT,Bing Chat,Bard,文心一言.
2. 若报错,请先将ChatGPT,EdgeGPT,BingImageCreator,GoogleBard,easy-ernie更新到最新版本.
3. 已知New Bing,文心一言有封号风险.
---
![Release](https://img.shields.io/badge/Release-0.1.1-blue)
---
## 介绍
一款基于Python-FastAPI框架,开发的多种Chat接口程序.
## 需求
1. 语言: Python3.8+.
2. 包: fastapi,python-multipart,uvicorn,asyncio,EdgeGPT,BingImageCreator,GoogleBard,easy-ernie
3. 其他: New Bing账户,Bard账户,文心一言账户.
## 配置(config.py)
详情进入文件查看.
## Cookie(cookie/)
1. 浏览器安装Cookie-Editor扩展.
2. 访问[Bing Chat](https://www.bing.com/chat)/[Bard](https://bard.google.com)/[文心一言](https://yiyan.baidu.com).
3. 在页面中点击扩展.
4. 点击扩展右下角的Export-Export as JSON
5. 将复制的内容粘贴到对应的Cookie文件.
## 接口文档
查看[Wiki](https://github.com/XiaoXinYo/Chat-API/wiki).  
提示: 在使用Chat前,请确保对应的Cookie已配置好,ChatGPT密钥需要在config.py文件中写.