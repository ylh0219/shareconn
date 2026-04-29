"""隐私路由器 - 根据内容敏感性决定使用云端或本地模型"""

import re
from app.config import settings
from app.utils.logger import logger


class PrivacyRouter:
    """
    隐私内容路由器
    检测输入内容中的敏感关键词，
    当匹配到敏感模式时自动路由至本地模型进行推理，
    确保隐私数据不上传至云端。
    """

    # 敏感关键词列表
    SENSITIVE_KEYWORDS: list[str] = [
        "机密", "内部", "保密", "私密", "涉密",
        "敏感", "不可外传", "仅限内部",
        "confidential", "classified", "internal only",
    ]

    # 敏感模式正则 (身份证、手机号等)
    SENSITIVE_PATTERNS: list[re.Pattern] = [
        re.compile(r'\d{17}[\dXx]'),             # 身份证号
        re.compile(r'1[3-9]\d{9}'),               # 手机号
        re.compile(r'\d{6}\d{4}[01]\d[0-3]\d'),  # 出生日期模式
    ]

    @classmethod
    def should_use_local(cls, content: str) -> bool:
        """
        判断内容是否应路由至本地模型

        Args:
            content: 待分析的文本内容

        Returns:
            True 表示应使用本地模型
        """
        if not settings.LOCAL_LLM_ENABLED:
            return False

        # 关键词匹配
        for keyword in cls.SENSITIVE_KEYWORDS:
            if keyword in content:
                logger.info(f"检测到敏感关键词 '{keyword}'，路由至本地模型")
                return True

        # 正则模式匹配
        for pattern in cls.SENSITIVE_PATTERNS:
            if pattern.search(content):
                logger.info("检测到敏感数据模式，路由至本地模型")
                return True

        return False
