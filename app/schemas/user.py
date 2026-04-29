"""用户相关请求/响应 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    display_name: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class Token(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 解析数据"""
    user_id: Optional[int] = None
    username: Optional[str] = None
