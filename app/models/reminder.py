"""提醒任务模型"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ReminderStatus(str, enum.Enum):
    """提醒状态"""
    SCHEDULED = "scheduled"    # 已安排
    SENT = "sent"              # 已发送
    READ = "read"              # 已读
    CANCELLED = "cancelled"    # 已取消


class Reminder(Base, TimestampMixin):
    """提醒任务表 - 稍后阅读提醒"""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    share_id: Mapped[int] = mapped_column(ForeignKey("shares.id"), nullable=False, index=True)

    # 提醒配置
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notify_channel: Mapped[str] = mapped_column(
        String(20), default="web", nullable=False
    )  # web / email / wechat

    # 状态
    status: Mapped[ReminderStatus] = mapped_column(
        Enum(ReminderStatus), default=ReminderStatus.SCHEDULED, nullable=False
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # 关联
    user = relationship("User", back_populates="reminders")
    share = relationship("Share", back_populates="reminders")

    def __repr__(self) -> str:
        return f"<Reminder(id={self.id}, remind_at={self.remind_at}, status={self.status})>"
