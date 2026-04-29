"""LLM 提供者工厂 - 实现云端/本地大模型的无缝切换"""

from langchain_openai import ChatOpenAI
from app.config import settings
from app.utils.logger import logger


class LLMProvider:
    """
    LLM 工厂类
    根据配置返回对应的 ChatModel 实例，
    统一使用 OpenAI 兼容协议 (ChatOpenAI)，
    支持通过 base_url 切换至 vLLM / LiteLLM / OneAPI 等网关。
    """

    _cloud_instance: ChatOpenAI | None = None
    _local_instance: ChatOpenAI | None = None

    @classmethod
    def get_chat_model(cls, use_local: bool = False) -> ChatOpenAI:
        """
        获取 LLM 实例 (带缓存)

        Args:
            use_local: 是否强制使用本地模型

        Returns:
            ChatOpenAI 实例
        """
        if use_local and settings.LOCAL_LLM_ENABLED:
            return cls._get_local_model()
        return cls._get_cloud_model()

    @classmethod
    def _get_cloud_model(cls) -> ChatOpenAI:
        """获取云端 LLM 实例"""
        if cls._cloud_instance is None:
            logger.info(
                f"初始化云端 LLM: model={settings.CLOUD_LLM_MODEL}, "
                f"base_url={settings.CLOUD_LLM_BASE_URL}"
            )
            cls._cloud_instance = ChatOpenAI(
                base_url=settings.CLOUD_LLM_BASE_URL,
                api_key=settings.CLOUD_LLM_API_KEY,
                model=settings.CLOUD_LLM_MODEL,
                temperature=0.3,
                max_retries=3,
                request_timeout=60,
                model_kwargs={"extra_body": {"enable_thinking": False}},
            )
        return cls._cloud_instance

    @classmethod
    def _get_local_model(cls) -> ChatOpenAI:
        """获取本地 LLM 实例 (vLLM / Ollama 等)"""
        if cls._local_instance is None:
            logger.info(
                f"初始化本地 LLM: model={settings.LOCAL_LLM_MODEL}, "
                f"base_url={settings.LOCAL_LLM_BASE_URL}"
            )
            cls._local_instance = ChatOpenAI(
                base_url=settings.LOCAL_LLM_BASE_URL,
                api_key="not-needed",
                model=settings.LOCAL_LLM_MODEL,
                temperature=0.3,
                max_retries=2,
                request_timeout=120,  # 本地模型可能更慢
            )
        return cls._local_instance

    @classmethod
    def reset(cls):
        """重置缓存的 LLM 实例 (用于配置更新)"""
        cls._cloud_instance = None
        cls._local_instance = None
