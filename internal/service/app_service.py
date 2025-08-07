import uuid
from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy
from injector import inject

from internal.model import App


@inject
@dataclass
class AppService:
    """应用服务逻辑"""
    db: SQLAlchemy

    def create_app(self) -> App:
        # 1.创建实体类实例
        app = App(
            name="测试机器人",
            account_id=uuid.uuid4(),
            icon="",
            description="这是一个简单的聊天机器人"
        )
        # 2.将实体加入 Session
        self.db.session.add(app)
        # 3.提交
        self.db.session.commit()
        return app

    def get_app(self, id: uuid.UUID) -> App:
        # SQLAlchemy 1.4+ 推荐用 session.get
        return self.db.session.get(App, id)

    def update_app(self, id: uuid.UUID, new_name: str = "聊天机器人") -> App:
        # 先查询出对象
        app = self.get_app(id)
        if not app:
            raise ValueError(f"找不到 ID={id} 的 App 实例")
        # 修改属性
        app.name = new_name
        # 提交
        self.db.session.commit()
        return app

    def delete_app(self, id: uuid.UUID) -> App:
        app = self.get_app(id)
        if not app:
            raise ValueError(f"找不到 ID={id} 的 App 实例")
        self.db.session.delete(app)
        self.db.session.commit()
        return app
