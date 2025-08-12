import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    UUID,
    String,
    Integer,
    DateTime,
    PrimaryKeyConstraint,
    Text,
    Index,
    text,
)

from internal.extension.database_extension import db
from sqlalchemy.dialects.postgresql import JSONB


class App(db.Model):
    """AI应用基础模型类"""
    __tablename__ = "app"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_id"),
        Index("idx_app_account_id", "account_id"),
    )

    id = Column(UUID, default=uuid.uuid4, nullable=False)
    account_id = Column(UUID, nullable=False)
    name = Column(String(255), default="", nullable=False)
    icon = Column(String(255), default="", nullable=False)
    description = Column(Text, default="", nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

class AppConfigVersion(db.Model):
    """应用配置版本历史表，用于存储草稿配置+历史发布配置"""
    __tablename__ = "app_config_version"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_config_version_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))  # 配置id
    app_id = Column(UUID, nullable=False)  # 关联应用id
    model_config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))  # 模型配置
    dialog_round = Column(Integer, nullable=False, server_default=text("0"))  # 鞋带上下文轮数
    preset_prompt = Column(Text, nullable=False, server_default=text("''::text"))  # 人设与回复逻辑
    tools = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))  # 应用关联的工具列表
    workflows = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))  # 应用关联的工作流列表
    datasets = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))  # 应用关联的知识库列表
    retrieval_config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))  # 检索配置
    long_term_memory = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))  # 长期记忆配置
    opening_statement = Column(Text, nullable=False, server_default=text("''::text"))  # 开场白文案
    opening_questions = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))  # 开场白建议问题列表
    speech_to_text = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))  # 语音转文本配置
    text_to_speech = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))  # 文本转语音配置
    review_config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))  # 审核配置
    version = Column(Integer, nullable=False, server_default=text("0"))  # 发布版本号
    config_type = Column(String(255), nullable=False, server_default=text("''::character varying"))  # 配置类型
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        server_onupdate=text("CURRENT_TIMESTAMP(0)"),
    )
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(0)"))