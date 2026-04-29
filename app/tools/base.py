"""解析工具基类"""

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class ParseResult(BaseModel):
    """统一解析结果结构"""
    title: Optional[str] = None
    author: Optional[str] = None
    content: str                             # 正文 / 字幕 / OCR 文本
    description: Optional[str] = None        # 简介
    duration_seconds: Optional[int] = None   # 视频时长(秒)
    cover_url: Optional[str] = None          # 封面图
    platform: str                            # 平台标识
    original_url: Optional[str] = None       # 原始 URL
    extra: Optional[dict] = None             # 平台特有额外信息


class BaseParseTool(ABC):
    """
    解析工具抽象基类
    所有平台解析器必须继承此类并实现 parse 方法。
    """
    name: str = "base_parser"
    description: str = "基础解析工具"
    platform: str = "unknown"

    @abstractmethod
    async def parse(self, url_or_content: str) -> ParseResult:
        """
        解析输入并返回结构化结果

        Args:
            url_or_content: URL 或原始内容

        Returns:
            ParseResult 结构化解析结果
        """
        ...

    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        """
        判断该工具是否能处理此 URL

        Args:
            url: 待检测的 URL

        Returns:
            True 表示该工具可以处理此 URL
        """
        ...
