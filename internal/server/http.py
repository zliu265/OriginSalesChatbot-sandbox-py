import os

from flask import Flask
from pkg.sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config
from internal.exception import CustomException
from internal.model import App
from internal.router import Router
from pkg.response import Response, json, HttpCode


class Http(Flask):
    # Http服务引擎
    # args是不命名参数，kwargs是命名参数
    def __init__(self, *args, conf: Config, db: SQLAlchemy,migrate: Migrate, router: Router, **kwargs):
        super().__init__(*args, **kwargs)
        # 注册应用路由
        self.config.from_object(conf)
        self.register_error_handler(Exception, self._register_error_handler)
        db.init_app(self)
        migrate.init_app(self, db, directory="internal/migration")
        with self.app_context():
            _ = App()
            db.create_all()
        router.register_router(self)

    def _register_error_handler(self, error: Exception):
        # 1. 异常信息是不是我们的自定义异常，如果是可以提取message和code等信息
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data
            ))
        # 2. 如果不是我们的自定义异常，则有可能是程序，数据库抛出的异常，也可以提取信息，设置未FAIL状态码
        if self.debug or os.getenv("FLASK_ENV") == "development":
            raise error
        else:
            return json(Response(
                code=HttpCode.FAIL,
                message=str(error),
                data={},
            ))