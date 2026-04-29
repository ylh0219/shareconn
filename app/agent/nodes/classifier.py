"""输入分类节点 - 分析用户输入类型和平台来源"""

import json
from langchain_core.messages import SystemMessage, HumanMessage

from app.agent.state import AgentState
from app.agent.prompts.classifier import CLASSIFIER_SYSTEM_PROMPT, CLASSIFIER_USER_TEMPLATE
from app.llm.provider import LLMProvider
from app.utils.url_detector import detect_platform, extract_urls, is_url
from app.utils.logger import logger


async def classify_input(state: AgentState) -> dict:
    """
    输入分类节点
    
    1. 先用规则引擎快速检测 (URL 正则匹配)
    2. 对于模糊情况 fallback 到 LLM 判断
    
    更新字段:
    - detected_platform
    - content_urls
    - input_type (可能修正)
    - current_step
    """
    raw_input = state["raw_input"]
    input_type = state.get("input_type", "text")
    
    logger.info(f"[分类节点] 开始分析输入, type={input_type}, len={len(raw_input)}")
    
    # 提取 URL
    urls = extract_urls(raw_input)
    
    # 如果输入本身就是一个 URL
    if not urls and is_url(raw_input.strip()):
        urls = [raw_input.strip()]
        input_type = "url"
    
    detected_platform = None
    
    if urls:
        # 规则引擎快速检测
        input_type = "url"
        detected_platform = detect_platform(urls[0])
        
        if detected_platform:
            logger.info(f"[分类节点] 规则匹配: platform={detected_platform}, url={urls[0][:80]}")
        else:
            detected_platform = "generic"
            logger.info(f"[分类节点] 未匹配特定平台，使用通用解析器: {urls[0][:80]}")
    
    elif input_type == "text":
        # 纯文本，无 URL
        detected_platform = None
        logger.info("[分类节点] 纯文本输入，无 URL")
    
    elif input_type == "image":
        detected_platform = None
        logger.info("[分类节点] 图片输入")
    
    return {
        "input_type": input_type,
        "detected_platform": detected_platform,
        "content_urls": urls,
        "current_step": "classified",
    }
