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

        bp.add_url_rule("/app", methods=["POST"], view_func=self.app_handler.create_app)
        bp.add_url_rule("/app/<uuid:id>", view_func=self.app_handler.get_app)
        bp.add_url_rule("/app/<uuid:id>", methods=["POST"], view_func=self.app_handler.update_app)
        bp.add_url_rule("/app/<uuid:id>/delete", methods=["POST"], view_func=self.app_handler.delete_app)

        bp.add_url_rule(
            "/apps/<uuid:app_id>/chat",
            methods=["POST"],
            view_func=self.app_handler.chat
        )

        # bp.add_url_rule(
        #     "/debug",
        #     view_func=self.app_handler.debug,
        #     methods=["POST"]
        # )

        # 新增的 /chat POST 路由
        bp.add_url_rule(
            "/chat",
            view_func=self.app_handler.chat,
            methods=["POST"]
        )

        bp.add_url_rule(
            "/chat/deepseek",
            view_func=self.app_handler.chatDeepseek,
            methods=["POST"]
        )


        app.register_blueprint(bp)
