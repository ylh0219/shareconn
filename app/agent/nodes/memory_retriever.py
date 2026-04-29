"""记忆检索节点 - 从向量库中搜索相关历史分享"""

from app.agent.state import AgentState
from app.memory.retriever import MemoryRetriever
from app.utils.logger import logger


async def retrieve_memory(state: AgentState) -> dict:
    """
    记忆检索节点
    
    将当前解析内容向量化后，在向量库中搜索相似的历史分享。
    检索结果注入到 Agent 状态中，供后续分析节点使用。
    
    更新字段:
    - related_memories
    - current_step
    """
    parsed_content = state.get("parsed_content", "")
    parsed_title = state.get("parsed_title", "")
    
    if not parsed_content:
        logger.warning("[记忆节点] 无解析内容，跳过记忆检索")
        return {
            "related_memories": [],
            "current_step": "memory_skipped",
        }
    
    # 构造检索文本: 标题 + 正文前 500 字
    search_text = f"{parsed_title or ''} {parsed_content[:500]}"
    
    logger.info(f"[记忆节点] 开始检索相关历史分享, 检索文本长度={len(search_text)}")
    
    try:
        memories = await MemoryRetriever.retrieve_related(
            text=search_text,
            top_k=5,
        )
        
        logger.info(f"[记忆节点] 找到 {len(memories)} 条相关记忆")
        
        return {
            "related_memories": memories,
            "current_step": "memory_retrieved",
        }
    
    except Exception as e:
        logger.error(f"[记忆节点] 记忆检索失败: {e}")
        return {
            "related_memories": [],
            "current_step": "memory_failed",
        }
