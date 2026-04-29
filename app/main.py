"""ShareConn (分享助手) - FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import v1_router
from app.api.websocket import router as ws_router
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # === 启动 ===
    logger.info(f"[启动] {settings.APP_NAME} 启动中... (env={settings.APP_ENV})")

    # 启动定时调度器
    try:
        from app.scheduler.reminder_jobs import start_scheduler, shutdown_scheduler
        start_scheduler()
    except Exception as e:
        logger.warning(f"[启动] 调度器启动失败 (非致命): {e}")
        shutdown_scheduler = None

    logger.info(f"[启动] {settings.APP_NAME} 启动完成")
    yield

    # === 关闭 ===
    logger.info(f"[关闭] {settings.APP_NAME} 关闭中...")
    if shutdown_scheduler:
        try:
            shutdown_scheduler()
        except Exception:
            pass
    logger.info(f"[关闭] {settings.APP_NAME} 已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="智能分享内容解析与管理助手 - 自动解析、分析、记忆您的分享",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(v1_router)
app.include_router(ws_router)


@app.get("/", tags=["根"])
async def root():
    """API 根路径"""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
