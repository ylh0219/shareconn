"""API v1 路由聚合"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.users import router as users_router
from app.api.v1.shares import router as shares_router
from app.api.v1.reminders import router as reminders_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(health_router)
v1_router.include_router(users_router)
v1_router.include_router(shares_router)
v1_router.include_router(reminders_router)
