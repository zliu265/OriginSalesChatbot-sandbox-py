# internal/handler/app_handler.py
import dotenv

from flask import request, jsonify
from internal.core.models.ollama_client import ollama_chat

dotenv.load_dotenv()

class AppHandler:
    """应用控制器"""
    def __init__(self):
        # 如果需要，可以把 host/model 改成从环境变量读
        self.host = "http://127.0.0.1:11434"
        self.model = "qwen3:8b"

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
        data = request.get_json() or {}
        prompt = data.get("prompt", "")

        reply = ollama_chat(prompt)
        return jsonify({"reply": reply})