"""提醒相关端点 - 创建、查询提醒"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.models.share import Share
from app.models.reminder import Reminder, ReminderStatus
from app.schemas.reminder import ReminderCreate, ReminderResponse, ReminderListResponse

router = APIRouter(prefix="/reminders", tags=["提醒"])


@router.post(
    "",
    response_model=ReminderResponse,
    status_code=201,
    summary="创建提醒",
)
async def create_reminder(
    reminder_in: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """为分享内容创建稍后阅读提醒"""
    # 验证分享记录存在且属于当前用户
    result = await db.execute(
        select(Share).where(
            Share.id == reminder_in.share_id,
            Share.user_id == current_user.id,
        )
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="分享记录不存在")

    reminder = Reminder(
        user_id=current_user.id,
        share_id=reminder_in.share_id,
        remind_at=reminder_in.remind_at,
        message=reminder_in.message,
        notify_channel=reminder_in.notify_channel,
    )
    db.add(reminder)
    await db.flush()
    await db.refresh(reminder)

    return reminder


@router.get(
    "",
    response_model=ReminderListResponse,
    summary="我的提醒列表",
)
async def list_reminders(
    status: ReminderStatus | None = Query(None, description="按状态筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """查询当前用户的提醒列表"""
    query = select(Reminder).where(Reminder.user_id == current_user.id)
    count_query = select(func.count(Reminder.id)).where(Reminder.user_id == current_user.id)

    if status:
        query = query.where(Reminder.status == status)
        count_query = count_query.where(Reminder.status == status)

    query = query.order_by(Reminder.remind_at.asc())

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    result = await db.execute(query)
    reminders = result.scalars().all()

    return ReminderListResponse(items=reminders, total=total)


@router.delete(
    "/{reminder_id}",
    status_code=204,
    summary="取消提醒",
)
async def cancel_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """取消提醒(标记为已取消)"""
    result = await db.execute(
        select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == current_user.id,
        )
    )
    reminder = result.scalar_one_or_none()

    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")

    reminder.status = ReminderStatus.CANCELLED
