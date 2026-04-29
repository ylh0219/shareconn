"""用户相关端点 - 注册、登录"""

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import create_access_token, get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/users", tags=["用户"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=UserResponse, status_code=201, summary="用户注册")
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """注册新用户"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建用户
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=pwd_context.hash(user_in.password),
        display_name=user_in.display_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db_session),
):
    """用户登录，返回 JWT Token"""
    result = await db.execute(select(User).where(User.username == user_in.username))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    token = create_access_token(user.id, user.username)

    return Token(access_token=token)


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的信息"""
    return current_user
