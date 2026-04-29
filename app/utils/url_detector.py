"""URL 平台检测工具 - 根据 URL 模式识别来源平台"""

import re
from typing import Optional


# 平台 URL 模式定义
PLATFORM_PATTERNS: dict[str, list[str]] = {
    "bilibili": [
        r"bilibili\.com",
        r"b23\.tv",
    ],
    "wechat": [
        r"mp\.weixin\.qq\.com",
        r"weixin\.qq\.com",
    ],
    "zhihu": [
        r"zhihu\.com",
        r"zhuanlan\.zhihu\.com",
    ],
    "douyin": [
        r"douyin\.com",
        r"v\.douyin\.com",
    ],
    "xiaohongshu": [
        r"xiaohongshu\.com",
        r"xhslink\.com",
    ],
    "weibo": [
        r"weibo\.com",
        r"m\.weibo\.cn",
    ],
}


def detect_platform(url: str) -> Optional[str]:
    """
    检测 URL 所属平台

    Args:
        url: 待检测的 URL 字符串

    Returns:
        平台标识 (bilibili / wechat / zhihu / ...) 或 None (通用网页)
    """
    url_lower = url.lower()
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return platform
    return None


def extract_urls(text: str) -> list[str]:
    """
    从文本中提取所有 URL

    Args:
        text: 可能包含 URL 的文本

    Returns:
        URL 列表
    """
    url_pattern = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]*[^\s<>"{}|\\^`\[\].,;:!?)\]]'
    )
    return url_pattern.findall(text)


def is_url(text: str) -> bool:
    """判断文本是否是一个 URL"""
    return bool(re.match(r'^https?://', text.strip()))
