"""分享相关请求/响应 Schema"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class InputType(str, Enum):
    """输入类型枚举"""
    URL = "url"
    TEXT = "text"
    IMAGE = "image"


class ShareCreate(BaseModel):
    """创建分享请求"""
    content: str = Field(..., description="URL / 纯文本 / base64 图片")
    input_type: InputType = Field(..., description="输入类型")
    sender_name: Optional[str] = Field(None, description="分享者名称")


class ShareAnalysisResult(BaseModel):
    """LLM 分析结果"""
    theme: str = Field(..., description="主题")
    summary: str = Field(..., description="摘要")
    importance: int = Field(..., ge=1, le=10, description="重要性 1-10")
    urgency: int = Field(..., ge=1, le=10, description="紧急程度 1-10")
    estimated_time_minutes: int = Field(..., ge=0, description="预估阅读/观看时长(分钟)")
    related_past_shares: list[str] = Field(default_factory=list, description="相关历史分享")
    source_platform: Optional[str] = Field(None, description="来源平台")


class ShareResponse(BaseModel):
    """分享记录响应"""
    id: int
    user_id: int
    raw_input: str
    input_type: str
    sender_name: Optional[str] = None
    source_platform: Optional[str] = None
    status: str

    # 解析结果
    parsed_title: Optional[str] = None
    parsed_author: Optional[str] = None

    # 分析结果
    theme: Optional[str] = None
    summary: Optional[str] = None
    importance: Optional[int] = None
    urgency: Optional[int] = None
    estimated_time_minutes: Optional[int] = None
    related_past_shares: Optional[list[str]] = None

    # 时间
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class ShareListResponse(BaseModel):
    """分享列表分页响应"""
    items: list[ShareResponse]
    total: int
    page: int
    page_size: int


class ShareTaskResponse(BaseModel):
    """提交分享后返回的任务 ID"""
    share_id: int
    status: str = "pending"
    message: str = "分享已提交，正在处理中"
