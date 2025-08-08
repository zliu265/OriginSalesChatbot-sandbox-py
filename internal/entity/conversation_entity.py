from enum import Enum

# 摘要汇总模板
SUMMARIZER_TEMPLATE = """逐步总结提供的对话内容，在之前的总结基础上继续添加并返回一个新的总结。

EXAMPLE
当前总结:
人类询问 AI 对人工智能的看法。AI 认为人工智能是一股向善的力量。

新的会话:
Human: 为什么你认为人工智能是一股向善的力量？
AI: 因为人工智能将帮助人类发挥他们全部的潜力。

新的总结:
人类询问AI对人工智能的看法，AI认为人工智能是一股向善的力量，因为它将帮助人类发挥全部潜力。
END OF EXAMPLE

当前总结:
{summary}

新的会话:
{new_lines}

新的总结:"""

class MessageStatus(str, Enum):
    """会话状态"""
    NORMAL = "normal"  # 正常
    STOP = "stop"  # 停止
    ERROR = "error"  # 出错