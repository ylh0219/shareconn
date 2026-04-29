"""分享处理异步任务 - Celery Worker 中执行"""

import asyncio
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.agent.graph import run_share_analysis
from app.memory.retriever import MemoryRetriever
from app.config import settings
from app.utils.logger import logger


def _get_fresh_db():
    """
    为每次 Celery 任务创建独立的 SQLAlchemy 引擎和会话工厂。
    
    这避免了 asyncio.run() 每次创建新事件循环时，
    与全局引擎中缓存的旧事件循环连接冲突的问题。
    """
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.pool import NullPool

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return engine, session_factory


@celery_app.task(bind=True, name="process_share", max_retries=3)
def process_share(self, share_id: int, raw_input: str, input_type: str):
    """
    异步处理分享内容的 Celery 任务

    1. 运行 LangGraph Agent 工作流
    2. 将分析结果更新到数据库
    3. 将内容存入向量记忆库

    Args:
        share_id: 分享记录 ID
        raw_input: 用户原始输入
        input_type: 输入类型
    """
    logger.info(f"[Celery] 开始处理分享: share_id={share_id}")

    try:
        # 在 Celery worker 中运行异步代码
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                _process(share_id, raw_input, input_type)
            )
        finally:
            loop.close()

        logger.info(f"[Celery] 分享处理完成: share_id={share_id}")
        return result

    except Exception as exc:
        logger.error(f"[Celery] 分享处理失败: share_id={share_id}, error={exc}")
        # 更新状态为失败
        fail_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(fail_loop)
        try:
            fail_loop.run_until_complete(_mark_failed(share_id, str(exc)))
        finally:
            fail_loop.close()
        # Celery 重试
        raise self.retry(exc=exc, countdown=60)


async def _process(share_id: int, raw_input: str, input_type: str) -> dict:
    """异步处理逻辑"""
    from sqlalchemy import update
    from app.models.share import Share, ShareStatus

    engine, session_factory = _get_fresh_db()

    try:
        # 1. 更新状态为处理中
        async with session_factory() as session:
            await session.execute(
                update(Share)
                .where(Share.id == share_id)
                .values(status=ShareStatus.PROCESSING)
            )
            await session.commit()

        # 2. 运行 Agent 工作流
        result = await run_share_analysis(raw_input, input_type)

        analysis = result.get("analysis_result", {})

        # 3. 更新数据库
        async with session_factory() as session:
            update_data = {
                "status": ShareStatus.COMPLETED,
                "parsed_title": result.get("parsed_title"),
                "parsed_author": result.get("parsed_author"),
                "parsed_content": result.get("parsed_content"),
                "parsed_metadata": result.get("parsed_metadata"),
                "source_platform": result.get("detected_platform"),
                "theme": analysis.get("theme"),
                "summary": analysis.get("summary"),
                "importance": analysis.get("importance"),
                "urgency": analysis.get("urgency"),
                "estimated_time_minutes": analysis.get("estimated_time_minutes"),
                "related_past_shares": analysis.get("related_past_shares", []),
                "completed_at": datetime.now(timezone.utc),
            }

            if result.get("error"):
                update_data["error_message"] = result["error"]

            await session.execute(
                update(Share).where(Share.id == share_id).values(**update_data)
            )
            await session.commit()

        # 4. 存储记忆
        if analysis.get("theme") and analysis.get("summary"):
            await MemoryRetriever.store_memory(
                share_id=share_id,
                theme=analysis["theme"],
                summary=analysis["summary"],
            )

        return {"share_id": share_id, "status": "completed", "analysis": analysis}

    finally:
        await engine.dispose()


async def _mark_failed(share_id: int, error_message: str):
    """标记分享处理失败"""
    from sqlalchemy import update
    from app.models.share import Share, ShareStatus

    engine, session_factory = _get_fresh_db()

    try:
        async with session_factory() as session:
            await session.execute(
                update(Share)
                .where(Share.id == share_id)
                .values(
                    status=ShareStatus.FAILED,
                    error_message=error_message,
                )
            )
            await session.commit()
    finally:
        await engine.dispose()
