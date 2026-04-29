"""APScheduler 提醒任务 - 定时扫描并推送到期提醒"""

from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, update

from app.utils.logger import logger

scheduler = AsyncIOScheduler()


async def check_and_send_reminders():
    """
    扫描到期提醒并发送通知

    每分钟执行一次，查找所有 status=scheduled 且 remind_at <= now 的提醒，
    将其标记为已发送，并通过 WebSocket / 其他渠道推送。
    """
    from app.db.session import async_session_factory
    from app.models.reminder import Reminder, ReminderStatus

    now = datetime.now(timezone.utc)

    async with async_session_factory() as session:
        # 查找到期提醒
        result = await session.execute(
            select(Reminder).where(
                Reminder.status == ReminderStatus.SCHEDULED,
                Reminder.remind_at <= now,
            )
        )
        reminders = result.scalars().all()

        if not reminders:
            return

        logger.info(f"[调度器] 发现 {len(reminders)} 条到期提醒")

        for reminder in reminders:
            try:
                # TODO: 通过 WebSocket / 邮件 / 微信 发送通知
                logger.info(
                    f"[调度器] 发送提醒: id={reminder.id}, "
                    f"user_id={reminder.user_id}, share_id={reminder.share_id}"
                )

                # 更新状态
                await session.execute(
                    update(Reminder)
                    .where(Reminder.id == reminder.id)
                    .values(
                        status=ReminderStatus.SENT,
                        sent_at=now,
                    )
                )

            except Exception as e:
                logger.error(f"[调度器] 提醒发送失败: id={reminder.id}, error={e}")

        await session.commit()


def start_scheduler():
    """启动定时调度器"""
    scheduler.add_job(
        check_and_send_reminders,
        trigger="interval",
        minutes=1,
        id="check_reminders",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[调度器] APScheduler 已启动")


def shutdown_scheduler():
    """关闭定时调度器"""
    scheduler.shutdown(wait=False)
    logger.info("[调度器] APScheduler 已关闭")
