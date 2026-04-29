"""用户模型"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """用户表 - 存储注册用户信息"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # 关联
    shares = relationship("Share", back_populates="user", lazy="selectin")
    reminders = relationship("Reminder", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
