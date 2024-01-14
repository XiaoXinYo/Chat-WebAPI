HTTP = {
    'host': '0.0.0.0', # HTTP地址
    'port': 222, # HTTP端口
    'ssl': {
        'enable': False, # 启用HTTP SSL
        'keyPath': '', # HTTP SSL Key路径
        'certPath': '' # HTTP SSL Cert路径
    }
}

PROXY = {
    'enable': False, # 启用代理
    'host': '', # 代理地址
    'port': 80, # 代理端口,
    'ssl': False # 启用代理SSL
}

CHATGPT_KEY = '' # ChatGPT密钥

TOKEN_USE_MAX_TIME_INTERVAL = 30 # Token使用最大时间间隔(分钟),超过此时间未使用将被删除