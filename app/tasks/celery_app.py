"""Celery 应用实例配置"""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "shareconn",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    # 序列化
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # 任务追踪
    task_track_started=True,
    # 超时
    task_time_limit=300,         # 5 分钟硬超时
    task_soft_time_limit=240,    # 4 分钟软超时
    # 重试
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # 结果
    result_expires=3600,         # 结果保留 1 小时
)

# 自动发现任务
celery_app.autodiscover_tasks(["app"])
celery_app.conf.update(include=['app.tasks.share_processing'])
