"""工具调用节点 - 根据分类结果选择并执行对应的解析器"""

from app.agent.state import AgentState
from app.tools import get_parser_for_url
from app.utils.logger import logger


async def execute_parser(state: AgentState) -> dict:
    """
    工具执行节点
    
    根据 detected_platform 和 content_urls 选择解析器并执行。
    对于纯文本输入，直接使用原文作为 parsed_content。
    
    更新字段:
    - parsed_title
    - parsed_author
    - parsed_content
    - parsed_metadata
    - current_step
    - error (解析失败时)
    """
    input_type = state.get("input_type", "text")
    raw_input = state["raw_input"]
    urls = state.get("content_urls", [])
    
    logger.info(f"[解析节点] input_type={input_type}, urls_count={len(urls)}")
    
    # 纯文本或图片输入，直接透传
    if input_type == "text" or not urls:
        logger.info("[解析节点] 纯文本输入，直接透传")
        return {
            "parsed_content": raw_input,
            "parsed_title": None,
            "parsed_author": None,
            "parsed_metadata": {"type": "text"},
            "current_step": "parsed",
        }
    
    # URL 输入，选择对应解析器
    url = urls[0]  # 目前只处理第一个 URL
    
    try:
        parser = get_parser_for_url(url)
        logger.info(f"[解析节点] 使用解析器: {parser.name}")
        
        result = await parser.parse(url)
        
        logger.info(
            f"[解析节点] 解析完成: title={result.title}, "
            f"content_len={len(result.content)}"
        )
        
        return {
            "parsed_title": result.title,
            "parsed_author": result.author,
            "parsed_content": result.content,
            "parsed_metadata": {
                "platform": result.platform,
                "description": result.description,
                "duration_seconds": result.duration_seconds,
                "cover_url": result.cover_url,
                "original_url": result.original_url,
                **(result.extra or {}),
            },
            "detected_platform": result.platform,
            "current_step": "parsed",
        }
    
    except Exception as e:
        error_msg = f"解析失败: {type(e).__name__}: {str(e)}"
        logger.error(f"[解析节点] {error_msg}")
        
        return {
            "parsed_content": f"[解析失败] 原始输入: {raw_input}",
            "parsed_title": None,
            "parsed_author": None,
            "parsed_metadata": {"error": str(e)},
            "error": error_msg,
            "current_step": "parse_failed",
        }
