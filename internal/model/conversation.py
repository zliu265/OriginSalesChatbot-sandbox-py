from sqlalchemy import (
    Column,
    UUID,
    String,
    Text,
    Integer,
    DateTime,
    Boolean,
    Numeric,
    Float,
    text,
    PrimaryKeyConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB

from internal.extension.database_extension import db

class Conversation(db.Model):
    """交流会话模型"""
    __tablename__ = "conversation"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_conversation_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    app_id = Column(UUID, nullable=False)  # 关联应用id
    name = Column(String(255), nullable=False, server_default=text("''::character varying"))  # 会话名称
    summary = Column(Text, nullable=False, server_default=text("''::text"))  # 会话摘要/长期记忆
    is_pinned = Column(Boolean, nullable=False, server_default=text("false"))  # 是否置顶
    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))  # 是否删除
    invoke_from = Column(String(255), nullable=False, server_default=text("''::character varying"))  # 调用来源
    created_by = Column(
        UUID,
        nullable=True,
    )  # 会话创建者，会随着invoke_from的差异记录不同的信息，其中web_app和debugger会记录账号id、service_api会记录终端用户id
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))


class Message(db.Model):
    """交流消息模型"""
    __tablename__ = "message"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_message_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))

    # 消息关联的记录
    app_id = Column(UUID, nullable=False)  # 关联应用id
    conversation_id = Column(UUID, nullable=False)  # 关联会话id
    invoke_from = Column(
        String(255),
        nullable=False,
        server_default=text("''::character varying"),
    )  # 调用来源，涵盖service_api、web_app、debugger等
    created_by = Column(UUID, nullable=False)  # 消息的创建来源，有可能是LLMOps的用户，也有可能是开放API的终端用户

    # 消息关联的原始问题
    query = Column(Text, nullable=False, server_default=text("''::text"))  # 用户提问的原始query
    message = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))  # 产生answer的消息列表
    message_token_count = Column(Integer, nullable=False, server_default=text("0"))  # 消息列表的token总数
    message_unit_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))  # 消息的单价
    message_price_unit = Column(Numeric(10, 4), nullable=False, server_default=text("0.0"))  # 消息的价格单位

    # 消息关联的答案信息
    answer = Column(Text, nullable=False, server_default=text("''::text"))  # Agent生成的消息答案
    answer_token_count = Column(Integer, nullable=False, server_default=text("0"))  # 消息答案的token数
    answer_unit_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))  # token的单位价格
    answer_price_unit = Column(Numeric(10, 4), nullable=False, server_default=text("0.0"))  # token的价格单位

    # 消息的相关统计信息
    latency = Column(Float, nullable=False, server_default=text("0.0"))  # 消息的总耗时
    is_deleted = Column(Boolean, nullable=False, server_default=text("false"))  # 软删除标记
    status = Column(String(255), nullable=False, server_default=text("''::character varying"))  # 消息的状态，涵盖正常、错误、停止
    error = Column(Text, nullable=False, server_default=text("''::text"))  # 发生错误时记录的信息
    total_token_count = Column(Integer, nullable=False, server_default=text("0"))  # 消耗的总token数，计算步骤的消耗
    total_price = Column(Numeric(10, 7), nullable=False, server_default=text("0.0"))  # 消耗的总价格，计算步骤的总消耗

    # 消息时间相关信息
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(0)'),
        server_onupdate=text('CURRENT_TIMESTAMP(0)'),
    )
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))

