import uuid

import dotenv
from dataclasses import dataclass
from operator import itemgetter
from typing import Any, Dict

from flask import request, jsonify
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
from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import validata_error_json, success_json, success_message

dotenv.load_dotenv()

@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService

    def create_app(self):
        """调用服务创建新的APP记录"""
        app = self.app_service.create_app()
        return success_message(f"应用已经成功创建，id为{app.id}")

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

    def chat(self):
        """
        POST /chat
        请求体 JSON: { "prompt": "...", "model": "可选" }
        返回 JSON:  { "reply": "模型返回内容" }
        """
        data = request.get_json() or {}
        prompt = data.get("prompt", "")
        model  = data.get("model", self.model)

        # 调用封装好的 Ollama 客户端
        reply = ollama_chat(prompt, model=model, host=self.host)
        return jsonify({"reply": reply})

    def chatDeepseek(self):
        req = CompletionReq()
        if not req.validate():
            return validata_error_json(req.errors)

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
        if configurable_memory is not None and isinstance(configurable_memory, BaseMemory):
            configurable_memory.save_context(run_obj.inputs, run_obj.outputs)

    def debug(self):
        req = CompletionReq()
        if not req.validate():
            return validata_error_json(req.errors)

        prompt = ChatPromptTemplate.from_message([
            ("system", "你是一个聊天机器人"),
            MessagesPlaceholder("history"),
            ("human", "{query}")
        ])

        memory = ConversationBufferWindowMemory(
            k = 3,
            input_key="query",
            output_key="output",
            return_messages=True,
            chat_memory=FileChatMessageHistory("./storage/memory/chat_history.txt")
        )

        llm = ChatOllama(
            model="qwen2.5:7b",
            base_url="http://localhost:11434"
        )

        chain = (RunnablePassthrough.assign(
            history=RunnableLambda(self._load_memory_variables) | itemgetter("history")
        ) | prompt | llm | StrOutputParser()).with_listeners(on_end=self._save_context)

        chain_input = {"query": req.query.data}
        content = chain.invoke(chain_input, config={"configurable": {"memory": memory}})

        return success_json({"content": content})