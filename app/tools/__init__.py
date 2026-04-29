"""解析工具注册表 - 管理所有可用的平台解析器"""

from app.tools.base import BaseParseTool, ParseResult
from app.tools.bilibili import BilibiliParserTool
from app.tools.wechat import WeChatArticleTool
from app.tools.generic_scraper import GenericScraperTool
from app.utils.logger import logger

# 工具注册表 (按优先级排序，通用解析器放最后作为兜底)
TOOL_REGISTRY: list[type[BaseParseTool]] = [
    BilibiliParserTool,
    WeChatArticleTool,
    GenericScraperTool,  # 兜底
]


def get_parser_for_url(url: str) -> BaseParseTool:
    """
    根据 URL 自动选择合适的解析工具

    Args:
        url: 待解析的 URL

    Returns:
        匹配到的解析工具实例
    """
    for tool_cls in TOOL_REGISTRY:
        if tool_cls.can_handle(url):
            logger.info(f"URL 匹配到解析器: {tool_cls.name} -> {url[:80]}")
            return tool_cls()

    # 不应走到这里，因为 GenericScraper 始终兜底
    logger.warning(f"未找到匹配的解析器，使用通用解析器: {url[:80]}")
    return GenericScraperTool()


def list_available_tools() -> list[dict]:
    """列出所有注册的解析工具信息"""
    return [
        {
            "name": tool_cls.name,
            "description": tool_cls.description,
            "platform": tool_cls.platform,
        }
        for tool_cls in TOOL_REGISTRY
    ]


__all__ = [
    "BaseParseTool",
    "ParseResult",
    "BilibiliParserTool",
    "WeChatArticleTool",
    "GenericScraperTool",
    "TOOL_REGISTRY",
    "get_parser_for_url",
    "list_available_tools",
]
