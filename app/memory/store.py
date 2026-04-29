"""向量存储抽象 - 支持 Qdrant 持久化和内存模式"""

from typing import Optional
from qdrant_client import QdrantClient, models
from app.config import settings
from app.utils.logger import logger


class VectorStore:
    """
    向量存储服务
    封装 Qdrant 客户端操作。
    MVP 阶段使用内存模式 (":memory:")，Phase 3 切换至持久化部署。
    """

    _client: QdrantClient | None = None
    VECTOR_SIZE = 1024  # text-embedding-v3 维度

    @classmethod
    def get_client(cls) -> QdrantClient:
        """获取 Qdrant 客户端 (单例)"""
        if cls._client is None:
            try:
                cls._client = QdrantClient(url=settings.QDRANT_URL, timeout=10)
                logger.info(f"已连接 Qdrant: {settings.QDRANT_URL}")
            except Exception:
                # Fallback 到内存模式
                logger.warning("Qdrant 连接失败，使用内存模式")
                cls._client = QdrantClient(":memory:")

            # 确保 collection 存在
            cls._ensure_collection()

        return cls._client

    @classmethod
    def _ensure_collection(cls):
        """确保向量 collection 存在，不存在则创建"""
        client = cls._client
        collection_name = settings.QDRANT_COLLECTION

        try:
            collections = client.get_collections().collections
            names = [c.name for c in collections]
            if collection_name not in names:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=cls.VECTOR_SIZE,
                        distance=models.Distance.COSINE,
                    ),
                )
                logger.info(f"创建向量 collection: {collection_name}")
        except Exception as e:
            logger.error(f"创建 collection 失败: {e}")

    @classmethod
    async def upsert(
        cls,
        point_id: int,
        vector: list[float],
        payload: dict,
    ):
        """
        插入或更新向量

        Args:
            point_id: 向量 ID (通常对应 share_id)
            vector: 向量数据
            payload: 关联的元数据 (theme, summary 等)
        """
        client = cls.get_client()
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        logger.debug(f"向量已存储: point_id={point_id}")

    @classmethod
    async def search(
        cls,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> list[dict]:
        """
        相似度搜索

        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            score_threshold: 最低相似度阈值

        Returns:
            匹配结果列表，包含 id, score, payload
        """
        client = cls.get_client()
        threshold = score_threshold or settings.MEMORY_SIMILARITY_THRESHOLD

        results = client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=query_vector,
            limit=top_k,
            score_threshold=threshold,
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results.points
        ]

    @classmethod
    def reset(cls):
        """重置客户端"""
        if cls._client:
            cls._client.close()
        cls._client = None
