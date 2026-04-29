"""综合分析节点 - LLM 分析并生成结构化报告"""

import json
from langchain_core.messages import SystemMessage, HumanMessage

from app.agent.state import AgentState
from app.agent.prompts.analyzer import (
    ANALYZER_SYSTEM_PROMPT,
    ANALYZER_USER_TEMPLATE,
    MEMORY_CONTEXT_TEMPLATE,
)
from app.llm.provider import LLMProvider
from app.llm.router import PrivacyRouter
from app.schemas.agent import AgentAnalysisOutput
from app.utils.logger import logger


async def analyze_content(state: AgentState) -> dict:
    """
    综合分析节点
    
    接收解析后的内容和历史记忆，调用 LLM 生成结构化分析报告。
    自动判断是否需要路由至本地模型（隐私路由）。
    
    更新字段:
    - analysis_result
    - current_step
    - messages
    """
    parsed_content = state.get("parsed_content", "")
    parsed_title = state.get("parsed_title", "未知标题")
    parsed_author = state.get("parsed_author", "未知作者")
    detected_platform = state.get("detected_platform", "unknown")
    related_memories = state.get("related_memories", [])
    
    logger.info(
        f"[分析节点] 开始分析: title={parsed_title}, "
        f"platform={detected_platform}, memories={len(related_memories)}"
    )
    
    # 构建记忆上下文
    memory_context = ""
    if related_memories:
        memory_lines = [
            f"  - [{m['theme']}] {m['summary']} (相似度: {m['similarity_score']})"
            for m in related_memories
        ]
        memory_context = MEMORY_CONTEXT_TEMPLATE.format(
            memories="\n".join(memory_lines)
        )
    
    # 截断过长内容 (LLM 上下文限制)
    max_content_len = 6000
    truncated_content = parsed_content[:max_content_len]
    if len(parsed_content) > max_content_len:
        truncated_content += f"\n\n... [内容已截断，原文共 {len(parsed_content)} 字]"
    
    # 构造消息
    user_message = ANALYZER_USER_TEMPLATE.format(
        platform=detected_platform,
        title=parsed_title or "未知",
        author=parsed_author or "未知",
        content=truncated_content,
        memory_context=memory_context,
    )
    
    messages = [
        SystemMessage(content=ANALYZER_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]
    
    # 隐私路由: 判断是否使用本地模型
    use_local = PrivacyRouter.should_use_local(parsed_content)
    llm = LLMProvider.get_chat_model(use_local=use_local)
    
    try:
        # 调用 LLM
        response = await llm.ainvoke(messages)
        response_text = response.content
        
        logger.debug(f"[分析节点] LLM 原始响应: {response_text[:200]}...")
        
        # 解析 JSON 响应
        analysis = _parse_analysis_response(response_text)
        
        logger.info(
            f"[分析节点] 分析完成: theme={analysis.get('theme')}, "
            f"importance={analysis.get('importance')}"
        )
        
        return {
            "analysis_result": analysis,
            "messages": messages + [response],
            "current_step": "analyzed",
        }
    
    except Exception as e:
        error_msg = f"LLM 分析失败: {type(e).__name__}: {str(e)}"
        logger.error(f"[分析节点] {error_msg}")
        
        return {
            "analysis_result": {
                "theme": "分析失败",
                "summary": f"无法完成分析: {str(e)}",
                "importance": 5,
                "urgency": 5,
                "estimated_time_minutes": 0,
                "key_points": [],
                "related_past_shares": [],
            },
            "error": error_msg,
            "current_step": "analysis_failed",
        }


def _parse_analysis_response(response_text: str) -> dict:
    """
    从 LLM 响应中解析 JSON
    处理可能的 markdown 代码块包裹情况
    """
    text = response_text.strip()
    
    # 去除 markdown 代码块标记
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        data = json.loads(text)
        # 使用 Pydantic 模型验证
        validated = AgentAnalysisOutput(**data)
        return validated.model_dump()
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"JSON 解析失败，尝试提取: {e}")
        
        # 尝试从文本中提取 JSON 片段
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                data = json.loads(json_match.group())
                validated = AgentAnalysisOutput(**data)
                return validated.model_dump()
            except Exception:
                pass
        
        # 最终 fallback
        return {
            "theme": "解析异常",
            "summary": response_text[:500],
            "importance": 5,
            "urgency": 5,
            "estimated_time_minutes": 5,
            "key_points": [],
            "related_past_shares": [],
        }
