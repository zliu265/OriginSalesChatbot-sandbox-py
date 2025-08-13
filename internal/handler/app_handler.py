import uuid

import dotenv
from dataclasses import dataclass
from operator import itemgetter
from typing import Any, Dict
from types import SimpleNamespace

from flask import request, jsonify
from flask_login import current_user
from injector import inject
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_core.memory import BaseMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableConfig
from langchain_core.tracers import Run

from internal.core.models import deepseek_chat
from internal.core.models.ollama_client import ollama_chat
from internal.entity.conversation_entity import InvokeFrom
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import validate_error_json, success_json, success_message

dotenv.load_dotenv()

@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService

    def create_app(self):
        """调用服务创建新的APP记录"""
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        query = req.query.data

        reply = deepseek_chat(query)
        app = self.app_service.create_app(name=query,description=reply)
        return success_message({
            "message": f"应用已经成功创建，id为{app.id}",
            "reply": reply
        })

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用已经成功获取，名称是{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用已经成功修改,修改的名字是{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"应用已经成功删除, id：{app.id}")

    def ping(self):
        return jsonify({"ping": "pong"})


    def chatDeepseek(self):
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        reply = deepseek_chat(req.query.data)
        return success_json({"reply": reply})

    @classmethod
    def _load_memory_variables(cls, input: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            return configurable_memory.load_memory_variables(input)
        return {"history": []}

    @classmethod
    def _save_context(cls, run_obj: Run, config: RunnableConfig) -> None:
        """存储对应的上下文信息到记忆实体中"""
        configurable = config.get("configurable", {})
        configurable_memory = configurable.get("memory", None)