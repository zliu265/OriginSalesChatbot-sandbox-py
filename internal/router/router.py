# internal/router/router.py
from injector import inject
from flask import Flask, Blueprint
from internal.handler.app_handler import AppHandler
from dataclasses import dataclass

@inject
@dataclass
class Router:
    app_handler: AppHandler

    def register_router(self, app: Flask):
        bp = Blueprint("llmops", __name__, url_prefix="")

        # 原有的 /ping
        bp.add_url_rule("/ping", view_func=self.app_handler.ping)

        # 新增的 /chat POST 路由
        bp.add_url_rule(
            "/chat",
            view_func=self.app_handler.chat,
            methods=["POST"]
        )


        app.register_blueprint(bp)
