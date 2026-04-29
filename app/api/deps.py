"""FastAPI 依赖注入 - 数据库 Session、当前用户等全局依赖"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.user import TokenData

security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Mock User for local integration testing"""
    result = await db.execute(select(User).where(User.id == 1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在 (请先执行 seed_test_user.py)",
        )
    return user


def create_access_token(user_id: int, username: str) -> str:
    """创建 JWT Access Token"""
    expire = datetime.now(timezone.utc).timestamp() + (
        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    payload = {
        "sub": user_id,
        "username": username,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """可选的用户认证 (未登录返回 None)"""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
