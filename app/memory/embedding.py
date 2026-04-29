"""Embedding 模型封装 - 将文本转化为向量"""

from langchain_openai import OpenAIEmbeddings
from app.config import settings
from app.utils.logger import logger


class EmbeddingService:
    """
    Embedding 服务
    使用 OpenAI 兼容的 Embedding API 将文本转化为向量。
    支持云端 & 本地 Embedding 模型。
    """

    _instance: OpenAIEmbeddings | None = None

    @classmethod
    def get_embeddings(cls) -> OpenAIEmbeddings:
        """获取 Embedding 模型实例 (单例)"""
        if cls._instance is None:
            logger.info(f"初始化 Embedding 模型: {settings.EMBEDDING_MODEL}")
            cls._instance = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.CLOUD_LLM_API_KEY,
                openai_api_base=settings.CLOUD_LLM_BASE_URL,
                check_embedding_ctx_length=False,
            )
        return cls._instance

    @classmethod
    async def embed_text(cls, text: str) -> list[float]:
        """
        将单段文本转化为向量

        Args:
            text: 待向量化的文本

        Returns:
            向量列表
        """
        embeddings = cls.get_embeddings()
        return await embeddings.aembed_query(text)

    @classmethod
    async def embed_texts(cls, texts: list[str]) -> list[list[float]]:
        """
        批量文本向量化

        Args:
            texts: 文本列表

        Returns:
            向量列表的列表
        """
        embeddings = cls.get_embeddings()
        return await embeddings.aembed_documents(texts)

    @classmethod
    def reset(cls):
        """重置缓存实例"""
        cls._instance = None
