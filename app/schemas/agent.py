"""Agent 输出结构化 Schema - 用于约束 LLM 输出格式"""

from pydantic import BaseModel, Field


class AgentAnalysisOutput(BaseModel):
    """Agent 综合分析节点的结构化输出格式"""

    theme: str = Field(..., description="内容主题，如'人工智能'、'美食探店'")
    summary: str = Field(..., description="100-300 字的内容摘要")
    importance: int = Field(
        ..., ge=1, le=10,
        description="重要性评分 1-10，10 为最重要"
    )
    urgency: int = Field(
        ..., ge=1, le=10,
        description="紧急程度 1-10，10 为最紧急"
    )
    estimated_time_minutes: int = Field(
        ..., ge=0,
        description="预估阅读/观看所需时间(分钟)"
    )
    related_past_shares: list[str] = Field(
        default_factory=list,
        description="与历史分享的关联描述列表"
    )
    key_points: list[str] = Field(
        default_factory=list,
        description="核心要点列表，3-5 条"
    )
