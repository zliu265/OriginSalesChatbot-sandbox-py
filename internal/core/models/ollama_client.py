# internal/client/ollama_client.py
import requests

def ollama_chat(
    prompt: str,
    model: str = "qwen3:8b",
    host: str = "http://127.0.0.1:11434"
) -> str:
    """
    向本地 Ollama 服务发送对话请求，返回模型的回复文本。
    """
    url = f"{host}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
