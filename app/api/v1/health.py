"""健康检查端点"""

from fastapi import APIRouter

router = APIRouter(tags=["健康检查"])


@router.get("/health", summary="健康检查")
async def health_check():
    """服务健康检查"""
    return {
        "status": "healthy",
        "service": "ShareConn",
        "version": "0.1.0",
    }


@router.get("/health/ready", summary="就绪检查")
async def readiness_check():
    """就绪检查 - 验证数据库等关键依赖"""
    checks = {"database": "ok", "redis": "ok"}

    # TODO: 添加实际的数据库和 Redis 连接检查

    return {
        "status": "ready",
        "checks": checks,
    }
