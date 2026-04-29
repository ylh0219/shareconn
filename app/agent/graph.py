"""LangGraph 状态图定义与编译 - Agent 工作流核心"""

from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes.classifier import classify_input
from app.agent.nodes.tool_executor import execute_parser
from app.agent.nodes.memory_retriever import retrieve_memory
from app.agent.nodes.analyzer import analyze_content
from app.utils.logger import logger


def build_share_agent():
    """
    构建分享分析 Agent 状态图

    工作流:
    classify → parse → retrieve_memory → analyze → END

    Returns:
        编译后的 LangGraph CompiledStateGraph
    """
    logger.info("构建 LangGraph Agent 工作流...")

    graph = StateGraph(AgentState)

    # 注册节点
    graph.add_node("classify", classify_input)
    graph.add_node("parse", execute_parser)
    graph.add_node("retrieve_memory", retrieve_memory)
    graph.add_node("analyze", analyze_content)

    # 定义边 (线性流程)
    graph.set_entry_point("classify")
    graph.add_edge("classify", "parse")
    graph.add_edge("parse", "retrieve_memory")
    graph.add_edge("retrieve_memory", "analyze")
    graph.add_edge("analyze", END)

    compiled = graph.compile()
    logger.info("Agent 工作流编译完成")

    return compiled


# 全局 Agent 实例 (懒加载)
_agent_instance = None


def get_share_agent():
    """获取全局 Agent 实例 (懒单例)"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = build_share_agent()
    return _agent_instance


async def run_share_analysis(raw_input: str, input_type: str = "url") -> dict:
    """
    运行分享分析工作流的便捷函数

    Args:
        raw_input: 用户原始输入 (URL / 文本)
        input_type: 输入类型

    Returns:
        分析结果字典
    """
    agent = get_share_agent()

    initial_state = {
        "raw_input": raw_input,
        "input_type": input_type,
        "content_urls": [],
        "detected_platform": None,
        "parsed_title": None,
        "parsed_author": None,
        "parsed_content": None,
        "parsed_metadata": None,
        "related_memories": [],
        "analysis_result": None,
        "messages": [],
        "error": None,
        "current_step": "started",
    }

    logger.info(f"开始分享分析: input_type={input_type}, input={raw_input[:80]}...")

    result = await agent.ainvoke(initial_state)

    logger.info(f"分享分析完成: step={result.get('current_step')}")

    return result
