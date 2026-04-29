"""记忆检索器 - 查找与当前内容相关的历史分享"""

from app.memory.embedding import EmbeddingService
from app.memory.store import VectorStore
from app.config import settings
from app.utils.logger import logger


class MemoryRetriever:
    """
    记忆检索服务
    将文本向量化后在向量库中搜索相似的历史分享，
    用于为 Agent 提供上下文关联。
    """

    @classmethod
    async def retrieve_related(
        cls,
        text: str,
        top_k: int = 5,
        threshold: float | None = None,
    ) -> list[dict]:
        """
        检索与给定文本相关的历史分享

        Args:
            text: 当前分享的文本内容 (主题 + 摘要)
            top_k: 返回数量
            threshold: 相似度阈值

        Returns:
            [{id, score, theme, summary}, ...]
        """
        try:
            # 1. 文本向量化
            vector = await EmbeddingService.embed_text(text)

            # 2. 向量搜索
            results = await VectorStore.search(
                query_vector=vector,
                top_k=top_k,
                score_threshold=threshold or settings.MEMORY_SIMILARITY_THRESHOLD,
            )

            logger.info(f"记忆检索: 找到 {len(results)} 条相关历史分享")

            # 3. 格式化返回
            return [
                {
                    "share_id": r["id"],
                    "similarity_score": round(r["score"], 4),
                    "theme": r["payload"].get("theme", ""),
                    "summary": r["payload"].get("summary", ""),
                }
                for r in results
            ]

        except Exception as e:
            logger.error(f"记忆检索失败: {e}")
            return []

    @classmethod
    async def store_memory(
        cls,
        share_id: int,
        theme: str,
        summary: str,
    ):
        """
        存储分享内容至记忆库

        Args:
            share_id: 分享记录 ID
            theme: 主题
            summary: 摘要
        """
        try:
            text = f"{theme}: {summary}"
            vector = await EmbeddingService.embed_text(text)

            await VectorStore.upsert(
                point_id=share_id,
                vector=vector,
                payload={
                    "theme": theme,
                    "summary": summary,
                    "share_id": share_id,
                },
            )
            logger.info(f"记忆已存储: share_id={share_id}, theme={theme}")

        except Exception as e:
            logger.error(f"存储记忆失败: {e}")
