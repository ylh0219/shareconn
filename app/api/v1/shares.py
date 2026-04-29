"""分享相关端点 - 提交分享、查询结果"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.models.share import Share, ShareStatus
from app.schemas.share import (
    ShareCreate,
    ShareResponse,
    ShareListResponse,
    ShareTaskResponse,
)
from app.tasks.share_processing import process_share
from app.utils.logger import logger

router = APIRouter(prefix="/shares", tags=["分享"])


@router.post(
    "",
    response_model=ShareTaskResponse,
    status_code=202,
    summary="提交分享",
)
async def create_share(
    share_in: ShareCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    提交分享内容进行分析

    - 创建分享记录 (status=pending)
    - 派发 Celery 异步任务
    - 返回任务 ID
    """
    # 创建分享记录
    share = Share(
        user_id=current_user.id,
        raw_input=share_in.content,
        input_type=share_in.input_type.value,
        sender_name=share_in.sender_name,
        status=ShareStatus.PENDING,
    )
    db.add(share)
    await db.flush()
    await db.refresh(share)

    logger.info(f"创建分享记录: id={share.id}, user={current_user.username}")

    # 派发异步任务
    process_share.delay(
        share_id=share.id,
        raw_input=share_in.content,
        input_type=share_in.input_type.value,
    )

    return ShareTaskResponse(
        share_id=share.id,
        status="pending",
        message="分享已提交，正在处理中",
    )


@router.get(
    "/{share_id}",
    response_model=ShareResponse,
    summary="查询分享详情",
)
async def get_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """查询分享记录详情及分析结果"""
    result = await db.execute(
        select(Share).where(Share.id == share_id, Share.user_id == current_user.id)
    )
    share = result.scalar_one_or_none()

    if not share:
        raise HTTPException(status_code=404, detail="分享记录不存在")

    return share


@router.get(
    "",
    response_model=ShareListResponse,
    summary="分享列表",
)
async def list_shares(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: ShareStatus | None = Query(None, description="按状态筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """分页查询当前用户的分享记录"""
    # 基础查询
    query = select(Share).where(Share.user_id == current_user.id)
    count_query = select(func.count(Share.id)).where(Share.user_id == current_user.id)

    # 状态筛选
    if status:
        query = query.where(Share.status == status)
        count_query = count_query.where(Share.status == status)

    # 总数
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = (
        query.order_by(Share.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    shares = result.scalars().all()

    return ShareListResponse(
        items=shares,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete(
    "/{share_id}",
    status_code=204,
    summary="删除分享",
)
async def delete_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """删除分享记录"""
    result = await db.execute(
        select(Share).where(Share.id == share_id, Share.user_id == current_user.id)
    )
    share = result.scalar_one_or_none()

    if not share:
        raise HTTPException(status_code=404, detail="分享记录不存在")

    await db.delete(share)
