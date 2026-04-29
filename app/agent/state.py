"""Agent 状态定义 - LangGraph StateGraph 的核心数据结构"""

from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Agent 工作流状态
    在图的各节点间传递，每个节点读取并更新相关字段。
    """

    # ===== 输入 =====
    raw_input: str                                    # 用户原始输入
    input_type: str                                   # url / text / image

    # ===== 分类结果 =====
    detected_platform: Optional[str]                  # bilibili / wechat / generic
    content_urls: list[str]                           # 提取出的 URL 列表

    # ===== 解析结果 =====
    parsed_title: Optional[str]                       # 解析标题
    parsed_author: Optional[str]                      # 解析作者
    parsed_content: Optional[str]                     # 解析后的纯文本内容
    parsed_metadata: Optional[dict]                   # 结构化元数据 (时长、封面等)

    # ===== 记忆 =====
    related_memories: list[dict]                      # 向量检索到的相似历史分享

    # ===== 最终输出 =====
    analysis_result: Optional[dict]                   # 最终结构化分析报告

    # ===== 流程控制 =====
    messages: Annotated[list, add_messages]           # LLM 消息历史
    error: Optional[str]                              # 错误信息
    current_step: Optional[str]                       # 当前处理步骤 (用于进度展示)
