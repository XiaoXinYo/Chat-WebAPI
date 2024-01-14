## 提示
1. 升级咯,此仓库前身为Bing-Chat,现已更名为Chat-WebAPI,支持多种Chat,现已支持Bard,Bing,ChatGPT,Claude,文心一言.
2. 已知Bing,文心一言有封号风险.
---
![Release](https://img.shields.io/badge/Release-0.1.8-blue)
---
## 介绍
一款基于Python-FastAPI框架,开发的多种Chat WebAPI程序.
## 需求
1. 平台: Windows/Linux/Docker.
2. 语言: Python3.8+.
3. 其他: Bard账户,Bing账户,ChatGPT密钥,Claude账户,文心一言账户.
## 配置
查看config.py文件.
## Cookie
1. 浏览器安装Cookie-Editor扩展.
2. 访问[Bard](https://bard.google.com/)/[Bing](https://www.bing.com/chat)/[Claude](https://claude.ai/)/[文心一言](https://yiyan.baidu.com/).
3. 在页面中点击扩展.
4. 点击扩展右下角的Export-Export as JSON
5. 将复制的内容粘贴到对应的Cookie文件(cookie/)中.
## 部署
1. Windows: 运行main.py文件.
2. Linux: 执行`gunicorn main:APP -c gunicorn.py`命令.
3. 支持Docker.
## 接口文档
查看[Wiki](https://github.com/XiaoXinYo/Chat-WebAPI/wiki).  
提示: 在使用Chat前,请确保对应的Cookie已配置好,ChatGPT密钥需要在config.py文件中写.