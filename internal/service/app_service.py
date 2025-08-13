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

    def chat_once(
            self,
            app_id:uuid.UUID,
            account,
            query:str,
            conversation_id: Optional[uuid.UUID] = None,
            invoke_from: InvokeFrom = InvokeFrom.END_USER,
    ) -> Tuple[Conversation, Message]:
        app = self.get_app(app_id, account)

        # 2) 读取配置（优先已发布；否则用草稿配置）
        # 如果你有 self.get_app_config 可用，优先使用；这里兜底到草稿
        cfg_version: AppConfigVersion = app.draft_app_config
        cfg = getattr(cfg_version, "model_config", None)
        dialog_round = getattr(cfg_version, "dialog_round", 3) or 3
        preset_prompt = getattr(cfg_version, "preset_prompt", "") or ""

        conversation = None
        if conversation_id:
            conversation = self.db.session.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.app_id == app.id
            ).one_or_none()
            if not conversation:
                raise FailException("conversation_id 不存在或不属于该 App")
        else:
            with self.db.auto_commit():
                conversation = Conversation(
                    app_id=app.id,
                    name="New Conversation",
                    invoke_from=invoke_from.value,
                    created_by=account.id,
                )
                self.db.session.add(conversation)
                self.db.session.flush()  # 获取 id

        with self.db.auto_commit():
            user_msg = Message(
                conversation_id=conversation.id,
                role=Role.USER.value,
                content=query,
                meta={}
            )
            self.db.session.add(user_msg)
        history: List[Message] = (
            self.db.session.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        messages = []
        if preset_prompt.strip():
            messages.append({"role": Role.SYSTEM.value, "content": preset_prompt.strip()})
        # 只携带最近 dialog_round 轮（user/assistant 对）
        if dialog_round and dialog_round > 0:
            # 取末尾 2 * dialog_round + 当前这条 user 的窗口
            tail = []
            for m in history[-(2 * dialog_round + 1):]:
                tail.append({"role": m.role, "content": m.content})
            messages.extend(tail)
        else:
            # 不限轮数（谨慎使用）
            for m in history:
                messages.append({"role": m.role, "content": m.content})
        # 6) 调用 LLM（根据 provider 切换）
        provider = (cfg.get("provider") or "openai").lower()
        model = cfg.get("model") or "gpt-4o-mini"
        params = cfg.get("parameters") or {}

        answer = self._call_llm(provider, model, params, messages)

        # 7) 写入助手消息
        with self.db.auto_commit():
            bot_msg = Message(
                conversation_id=conversation.id,
                role=Role.ASSISTANT.value,
                content=answer,
                meta={"provider": provider, "model": model}
            )
            self.db.session.add(bot_msg)

        # 8) 发送出去（可根据你的通道替换：WebSocket / 企业微信 / Webhook）
        try:
            self._notify_outbound(app, conversation, bot_msg)
        except Exception:
            # 不因发送失败影响主流程
            pass

        return conversation, bot_msg

    # --- 私有方法 ---

    def _call_llm(self, provider: str, model: str, params: dict, messages: list) -> str:
        """
        按 provider 路由到不同实现。
        """
        temperature = params.get("temperature", 0.5)
        top_p = params.get("top_p", 0.85)
        max_tokens = params.get("max_tokens", 8192)

        # if provider == "openai":
        #     # 读取 OPENAI_API_KEY from env
        #     client = OpenAI()
        #     resp = client.chat.completions.create(
        #         model=model,
        #         messages=messages,
        #         temperature=temperature,
        #         top_p=top_p,
        #         max_tokens=max_tokens,
        #     )
        #     return resp.choices[0].message.content or ""

        if provider == "ollama":
            # 默认本地 Ollama 服务
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            url = f"{base_url}/api/chat"
            payload = {
                "model": model,
                "messages": messages,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            r = requests.post(url, json=payload, timeout=180)
            r.raise_for_status()
            data = r.json()
            # /api/chat 流模式 & 非流模式结构不同，这里兼容常见非流模式
            if isinstance(data, dict) and "message" in data and "content" in data["message"]:
                return data["message"]["content"]
            # 有的实现会返回完整历史，取最后一条 assistant
            if isinstance(data, dict) and "messages" in data:
                for m in reversed(data["messages"]):
                    if m.get("role") == "assistant":
                        return m.get("content", "")
            return ""

        # 其他 provider 可在此扩展（dashscope、together 等）
        raise FailException(f"不支持的 provider: {provider}")

    def _notify_outbound(self, app: App, conv: Conversation, msg: Message) -> None:
        """
        把消息“发送出去”。这里留空实现，你可以：
        - 推 WebSocket/SSE 给前端
        - 调企业微信/钉钉/Slack Webhook
        - 写一张 outbox 表让异步任务消费
        """
        # 示例：print 或打日志；正式环境请接入你的通知通道
        print(f"[notify] app={app.id} conv={conv.id} -> {msg.content[:80]}")