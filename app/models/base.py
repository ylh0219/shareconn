"""SQLAlchemy 声明式基类"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    """所有 ORM 模型的基类，包含通用时间戳字段"""
    pass


class TimestampMixin:
    """通用时间戳 Mixin，自动管理 created_at 和 updated_at"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
