import uuid
import os
import requests

from typing import Optional, Tuple, List
from dataclasses import dataclass
from pkg.sqlalchemy import SQLAlchemy

from internal.entity.conversation_entity import InvokeFrom, Role
from internal.exception import FailException
from internal.model.app import App, AppConfigVersion
from internal.model.conversation import Conversation, Message
from injector import inject


@inject
@dataclass
class AppService:
    """应用服务逻辑"""
    db: SQLAlchemy

    def create_app(self, name: str, description: str) -> App:
        with self.db.auto_commit():
            # 1.创建模型的实力类
            app = App(
                name=name,
                account_id=uuid.uuid4(),
                icon="",
                description=description
            )
            # 2.将实体类添加到session会话中
            self.db.session.add(app)
            self.db.session.flush()
        return app

    def get_app(self, id: uuid.UUID) -> App:
        # SQLAlchemy 1.4+ 推荐用 session.get
        return self.db.session.get(App, id)

    def update_app(self, id: uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "聊天机器人"
        return app

    def delete_app(self, id: uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        return app
