"""全局配置管理 - 基于 pydantic-settings，支持 .env 文件加载"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置，所有配置项均可通过环境变量或 .env 文件覆盖"""

    # ===== 应用 =====
    APP_NAME: str = "Share Helper"
    APP_ENV: str = "development"  # development / staging / production
    DEBUG: bool = True

    # ===== 数据库 =====
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/sharehelper"

    # ===== Redis =====
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ===== LLM - 云端 =====
    CLOUD_LLM_BASE_URL: str = "https://api.openai.com/v1"
    CLOUD_LLM_API_KEY: str = ""
    CLOUD_LLM_MODEL: str = "gpt-4o"

    # ===== LLM - 本地 =====
    LOCAL_LLM_ENABLED: bool = False
    LOCAL_LLM_BASE_URL: str = "http://localhost:8000/v1"
    LOCAL_LLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct-AWQ"

    # ===== 向量数据库 =====
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "share_memories"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    MEMORY_SIMILARITY_THRESHOLD: float = 0.85

    # ===== 安全 =====
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
