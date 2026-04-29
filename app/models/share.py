"""分享记录模型 - 核心业务表"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ShareStatus(str, enum.Enum):
    """分享处理状态"""
    PENDING = "pending"          # 等待处理
    PROCESSING = "processing"    # 处理中
    COMPLETED = "completed"      # 完成
    FAILED = "failed"            # 失败


class Share(Base, TimestampMixin):
    """分享记录表 - 存储用户提交的分享内容及分析结果"""

    __tablename__ = "shares"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # 输入信息
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    input_type: Mapped[str] = mapped_column(String(20), nullable=False)  # url / text / image
    sender_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # 处理状态
    status: Mapped[ShareStatus] = mapped_column(
        Enum(ShareStatus), default=ShareStatus.PENDING, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 解析后的原始内容
    parsed_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    parsed_author: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    parsed_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # LLM 分析结果
    theme: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    importance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    urgency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    related_past_shares: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # 时间戳
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # 关联
    user = relationship("User", back_populates="shares")
    reminders = relationship("Reminder", back_populates="share", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Share(id={self.id}, status={self.status}, platform={self.source_platform})>"
