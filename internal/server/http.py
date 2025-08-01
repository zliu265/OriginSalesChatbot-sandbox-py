from flask import Flask

from internal.router import Router


class Http(Flask):
    # Http服务引擎
    # args是不命名参数，kwargs是命名参数
    def __init__(self, *args, router: Router, **kwargs):
        super().__init__(*args, **kwargs)
        # 注册应用路由
        router.register_router(self)