"""提醒相关请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReminderCreate(BaseModel):
    """创建提醒请求"""
    share_id: int = Field(..., description="关联的分享记录 ID")
    remind_at: datetime = Field(..., description="提醒时间")
    message: Optional[str] = Field(None, description="自定义提醒内容")
    notify_channel: str = Field("web", description="通知渠道: web / email / wechat")


class ReminderResponse(BaseModel):
    """提醒响应"""
    id: int
    user_id: int
    share_id: int
    remind_at: datetime
    message: Optional[str] = None
    notify_channel: str
    status: str
    sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReminderListResponse(BaseModel):
    """提醒列表响应"""
    items: list[ReminderResponse]
    total: int
