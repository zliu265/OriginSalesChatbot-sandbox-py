import os
import requests


def deepseek_chat(
    query: str,
    prompt: str,
    model: str = "deepseek-chat",
    api_key: str | None = None,
    base_url: str = "https://api.deepseek.com/v1",
) -> str:
    """调用 Deepseek API 发送对话请求并返回回复内容。"""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Deepseek API key is required")

    url = f"{base_url}/chat/completions"
    prompt = "You are a helpful assistant."
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt },
            {"role": "user", "content": query}
        ],
        # "stream": false,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]