# Share Helper (分享助手) — Python 系统架构设计

## 1. 设计文档分析

### 1.1 核心业务目标

系统的核心价值链可归纳为：

```
接收分享 → 识别平台 → 解析内容 → LLM 分析 → 记忆关联 → 结构化输出 → 提醒推送
```

### 1.2 关键技术挑战

| 挑战领域 | 具体问题 | 设计文档选型 |
|---------|---------|------------|
| 多平台解析 | 知乎/B站/抖音/微信各有反爬策略 | 独立 Parser 微服务 |
| 长任务异步 | 音视频解析耗时数十秒 | Celery / Redis Queue |
| LLM 多模式 | 云端 API 与本地 vLLM 无缝切换 | LangChain 抽象 + LiteLLM |
| 语义记忆 | 历史分享的向量检索与关联 | Milvus / Qdrant |
| 高可用扩展 | 突发流量下自动扩缩容 | K8s HPA |

### 1.3 分阶段交付策略

设计文档明确了 **3 阶段迭代路径**：

1. **Phase 1 (MVP)**: FastAPI + LangGraph + 外部 LLM API + 基础 Web UI
2. **Phase 2 (分布式)**: vLLM 本地模型 + Celery 异步 + K8s 部署
3. **Phase 3 (生态扩展)**: 向量数据库记忆 + 小程序/APP 多端

> [!IMPORTANT]
> 以下架构设计以 **Phase 1 (MVP)** 为落地目标，同时在代码结构上预留 Phase 2/3 的扩展接口，避免后续重构。

---

## 2. 技术栈选型

| 层级 | 技术选型 | 版本 | 说明 |
|-----|---------|------|------|
| Web 框架 | FastAPI | 0.115+ | 高性能异步支持，自动生成 OpenAPI 文档 |
| Agent 引擎 | LangGraph | 0.3+ | 状态图编排多步推理工作流 |
| LLM 抽象 | LangChain | 0.3+ | `ChatOpenAI` 封装，兼容 OpenAI 协议 |
| 任务队列 | Celery + Redis | 5.4+ | MVP 阶段使用 Redis 作为 Broker |
| 关系数据库 | PostgreSQL | 16 | 用户数据、分享记录、提醒任务 |
| ORM | SQLAlchemy | 2.0+ | 异步 Session 支持 |
| 数据迁移 | Alembic | 1.13+ | 数据库版本管理 |
| 向量数据库 | Qdrant | 1.9+ | Phase 3，记忆检索（MVP 阶段可用内存模式） |
| 定时任务 | APScheduler | 3.10+ | 稍后阅读提醒推送 |
| HTTP 客户端 | httpx | 0.27+ | 异步解析各平台内容 |
| 无头浏览器 | Playwright | 1.44+ | 应对 JS 渲染型页面（知乎等） |
| 配置管理 | pydantic-settings | 2.3+ | `.env` 分环境配置 |
| 容器化 | Docker + docker-compose | — | 本地开发全家桶一键启动 |

---

## 3. 项目目录结构

```
ShareConn/
├── docker-compose.yml              # 本地开发编排 (FastAPI + Redis + PostgreSQL + Qdrant)
├── Dockerfile                      # 应用镜像
├── pyproject.toml                  # 项目元数据与依赖 (Poetry/uv)
├── alembic.ini                     # 数据库迁移配置
├── .env.example                    # 环境变量模板
│
├── alembic/                        # 数据库迁移脚本
│   ├── env.py
│   └── versions/
│
├── app/                            # 应用主包
│   ├── __init__.py
│   ├── main.py                     # FastAPI 应用入口 & 生命周期管理
│   ├── config.py                   # pydantic-settings 全局配置
│   │
│   ├── api/                        # API 路由层
│   │   ├── __init__.py
│   │   ├── deps.py                 # 依赖注入 (DB Session, 当前用户等)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py           # v1 路由聚合
│   │   │   ├── shares.py           # 分享相关端点
│   │   │   ├── users.py            # 用户相关端点
│   │   │   ├── reminders.py        # 提醒相关端点
│   │   │   └── health.py           # 健康检查
│   │   └── websocket.py            # WebSocket 实时推送
│   │
│   ├── models/                     # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── base.py                 # DeclarativeBase
│   │   ├── user.py
│   │   ├── share.py                # 分享记录表
│   │   └── reminder.py             # 提醒任务表
│   │
│   ├── schemas/                    # Pydantic 请求/响应 Schema
│   │   ├── __init__.py
│   │   ├── share.py
│   │   ├── user.py
│   │   ├── reminder.py
│   │   └── agent.py                # Agent 输出结构化 Schema
│   │
│   ├── db/                         # 数据库连接与会话管理
│   │   ├── __init__.py
│   │   └── session.py              # async engine + sessionmaker
│   │
│   ├── agent/                      # 🧠 LangGraph 智能体引擎 (核心)
│   │   ├── __init__.py
│   │   ├── graph.py                # StateGraph 定义与编译
│   │   ├── state.py                # AgentState TypedDict
│   │   ├── nodes/                  # 图节点实现
│   │   │   ├── __init__.py
│   │   │   ├── classifier.py       # 输入分类节点
│   │   │   ├── tool_executor.py    # 工具调用节点
│   │   │   ├── memory_retriever.py # 记忆检索节点
│   │   │   └── analyzer.py         # 综合分析节点
│   │   └── prompts/                # Prompt 模板
│   │       ├── classifier.py
│   │       └── analyzer.py
│   │
│   ├── tools/                      # Agent 可调用的工具集
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseParseTool 抽象
│   │   ├── zhihu.py                # ZhihuParserTool
│   │   ├── bilibili.py             # BilibiliParserTool
│   │   ├── douyin.py               # DouyinParserTool
│   │   ├── wechat.py               # WeChatArticleTool
│   │   ├── image_ocr.py            # ImageOCRTool
│   │   └── generic_scraper.py      # 通用网页抓取
│   │
│   ├── llm/                        # LLM 提供者抽象层
│   │   ├── __init__.py
│   │   ├── provider.py             # LLMProvider 工厂 (云端/本地切换)
│   │   └── router.py               # 隐私路由 (敏感内容 → 本地模型)
│   │
│   ├── memory/                     # 向量记忆模块
│   │   ├── __init__.py
│   │   ├── embedding.py            # Embedding 模型封装
│   │   ├── store.py                # 向量存储抽象 (Qdrant / 内存)
│   │   └── retriever.py            # Top-K 检索 + 相似度阈值过滤
│   │
│   ├── tasks/                      # Celery 异步任务
│   │   ├── __init__.py
│   │   ├── celery_app.py           # Celery 实例配置
│   │   └── share_processing.py     # 分享处理异步任务
│   │
│   ├── scheduler/                  # 定时任务调度
│   │   ├── __init__.py
│   │   └── reminder_jobs.py        # APScheduler 提醒推送任务
│   │
│   └── utils/                      # 公共工具
│       ├── __init__.py
│       ├── url_detector.py         # URL 平台识别
│       └── logger.py               # 结构化日志配置
│
├── tests/                          # 测试
│   ├── conftest.py
│   ├── test_api/
│   ├── test_agent/
│   └── test_tools/
│
└── frontend/                       # 前端 (Phase 1 简易 Web UI)
    └── ...                         # 前端代码 (建议 Vite + React/Vue)
```

---

## 4. 核心模块详细设计

### 4.1 API 层设计 (`app/api/`)

#### 核心端点

| 方法 | 路径 | 说明 | 返回 |
|-----|------|------|------|
| `POST` | `/api/v1/shares` | 提交分享内容（URL/文本/图片） | 任务 ID |
| `GET` | `/api/v1/shares/{id}` | 查询分享分析结果 | 分析报告 JSON |
| `GET` | `/api/v1/shares` | 列出用户所有分享记录 | 分页列表 |
| `POST` | `/api/v1/reminders` | 创建稍后阅读提醒 | 提醒 ID |
| `GET` | `/api/v1/reminders` | 查询用户待处理提醒 | 提醒列表 |
| `WS` | `/ws/shares/{id}` | 实时推送解析进度 | 流式事件 |

#### 请求/响应 Schema 示例

```python
# app/schemas/share.py
from pydantic import BaseModel, HttpUrl
from enum import Enum
from typing import Optional

class InputType(str, Enum):
    URL = "url"
    TEXT = "text"
    IMAGE = "image"

class ShareCreate(BaseModel):
    content: str                    # URL / 纯文本 / base64 图片
    input_type: InputType
    sender_name: Optional[str] = None  # 分享者名称

class ShareAnalysisResult(BaseModel):
    theme: str
    summary: str
    importance: int                 # 1-10
    urgency: int                    # 1-10
    estimated_time_minutes: int
    related_past_shares: list[str]
    source_platform: Optional[str] = None
```

---

### 4.2 LangGraph Agent 工作流 (`app/agent/`)

这是系统的**核心大脑**，采用 LangGraph 的 StateGraph 实现有状态的多步推理。

#### 状态定义

```python
# app/agent/state.py
from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 输入
    raw_input: str                          # 用户原始输入
    input_type: str                         # url / text / image
    
    # 分类结果
    detected_platform: Optional[str]        # zhihu / bilibili / douyin / wechat / generic
    
    # 解析结果
    parsed_content: Optional[str]           # 解析后的纯文本内容
    metadata: Optional[dict]               # 标题、作者、时长等结构化元数据
    
    # 记忆
    related_memories: list[dict]            # 相似历史分享
    
    # 最终输出
    analysis_result: Optional[dict]         # 最终结构化分析报告
    
    # 流程控制
    messages: Annotated[list, add_messages] # LLM 消息历史
    error: Optional[str]                    # 错误信息
```

#### 状态图流程

```mermaid
graph TD
    A["__start__"] --> B["Input Classifier"]
    B --> C{"Platform?"}
    C -->|zhihu| D1["ZhihuParser"]
    C -->|bilibili| D2["BilibiliParser"]
    C -->|douyin| D3["DouyinParser"]
    C -->|wechat| D4["WeChatParser"]
    C -->|image| D5["ImageOCR"]
    C -->|text/generic| D6["GenericScraper/PassThrough"]
    D1 --> E["Memory Retriever"]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    E --> F["Analyzer"]
    F --> G["__end__"]
```

#### 图编译示例

```python
# app/agent/graph.py
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import classifier, tool_executor, memory_retriever, analyzer

def build_share_agent() -> StateGraph:
    graph = StateGraph(AgentState)
    
    # 添加节点
    graph.add_node("classify", classifier.classify_input)
    graph.add_node("parse", tool_executor.execute_parser)
    graph.add_node("retrieve_memory", memory_retriever.retrieve)
    graph.add_node("analyze", analyzer.analyze)
    
    # 定义边
    graph.set_entry_point("classify")
    graph.add_edge("classify", "parse")
    graph.add_edge("parse", "retrieve_memory")
    graph.add_edge("retrieve_memory", "analyze")
    graph.add_edge("analyze", END)
    
    return graph.compile()
```

---

### 4.3 LLM 提供者抽象层 (`app/llm/`)

实现设计文档要求的**双模兼容**（云端 API / 本地 vLLM）。

```python
# app/llm/provider.py
from langchain_openai import ChatOpenAI
from app.config import settings

class LLMProvider:
    """LLM 工厂，根据配置返回对应的 ChatModel 实例"""
    
    @staticmethod
    def get_chat_model(use_local: bool = False) -> ChatOpenAI:
        if use_local and settings.LOCAL_LLM_ENABLED:
            return ChatOpenAI(
                base_url=settings.LOCAL_LLM_BASE_URL,  # e.g. http://vllm:8000/v1
                api_key="not-needed",
                model=settings.LOCAL_LLM_MODEL,
                temperature=0.3,
            )
        return ChatOpenAI(
            base_url=settings.CLOUD_LLM_BASE_URL,
            api_key=settings.CLOUD_LLM_API_KEY,
            model=settings.CLOUD_LLM_MODEL,
            temperature=0.3,
        )
```

```python
# app/llm/router.py
class PrivacyRouter:
    """根据内容敏感性路由至本地或云端模型"""
    SENSITIVE_KEYWORDS = ["机密", "内部", "保密", "私人"]
    
    @classmethod
    def should_use_local(cls, content: str) -> bool:
        return any(kw in content for kw in cls.SENSITIVE_KEYWORDS)
```

---

### 4.4 工具层设计 (`app/tools/`)

每个平台解析器实现统一的 `BaseParseTool` 接口：

```python
# app/tools/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

class ParseResult(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    content: str                    # 正文/字幕/OCR文本
    duration_seconds: Optional[int] = None  # 视频时长
    platform: str
    original_url: Optional[str] = None

class BaseParseTool(ABC):
    name: str
    description: str
    
    @abstractmethod
    async def parse(self, url_or_content: str) -> ParseResult:
        """解析输入并返回结构化结果"""
        ...
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        """判断该工具是否能处理此 URL"""
        ...
```

```python
# app/tools/bilibili.py (示例)
import httpx
from app.tools.base import BaseParseTool, ParseResult

class BilibiliParserTool(BaseParseTool):
    name = "bilibili_parser"
    description = "解析 B 站视频，提取标题、UP主、简介、字幕和时长"
    
    PATTERNS = ["bilibili.com", "b23.tv"]
    
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return any(p in url for p in cls.PATTERNS)
    
    async def parse(self, url: str) -> ParseResult:
        bvid = self._extract_bvid(url)
        async with httpx.AsyncClient() as client:
            # 1. 获取视频信息
            info = await client.get(
                f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            )
            data = info.json()["data"]
            
            # 2. 尝试获取字幕
            subtitle_text = await self._fetch_subtitle(client, bvid, data["cid"])
            
            return ParseResult(
                title=data["title"],
                author=data["owner"]["name"],
                content=subtitle_text or data["desc"],
                duration_seconds=data["duration"],
                platform="bilibili",
                original_url=url,
            )
```

---

### 4.5 数据模型 (`app/models/`)

```python
# app/models/share.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base

class ShareStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Share(Base):
    __tablename__ = "shares"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    raw_input = Column(Text, nullable=False)
    input_type = Column(String(20), nullable=False)        # url / text / image
    sender_name = Column(String(100), nullable=True)       # 谁分享的
    source_platform = Column(String(50), nullable=True)    # bilibili / zhihu ...
    status = Column(Enum(ShareStatus), default=ShareStatus.PENDING)
    
    # 分析结果
    theme = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    importance = Column(Integer, nullable=True)
    urgency = Column(Integer, nullable=True)
    estimated_time_minutes = Column(Integer, nullable=True)
    related_past_shares = Column(JSON, nullable=True)
    
    parsed_content = Column(Text, nullable=True)           # 解析后的原文
    metadata_json = Column(JSON, nullable=True)            # 结构化元数据
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="shares")
    reminders = relationship("Reminder", back_populates="share")
```

---

### 4.6 异步任务处理 (`app/tasks/`)

```python
# app/tasks/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "share_helper",
    broker=settings.CELERY_BROKER_URL,       # redis://redis:6379/0
    backend=settings.CELERY_RESULT_BACKEND,  # redis://redis:6379/1
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=300,  # 5分钟超时
)
```

```python
# app/tasks/share_processing.py
from app.tasks.celery_app import celery_app
from app.agent.graph import build_share_agent

@celery_app.task(bind=True, max_retries=3)
def process_share(self, share_id: int, raw_input: str, input_type: str):
    """异步处理分享内容的 Celery 任务"""
    import asyncio
    
    async def _run():
        agent = build_share_agent()
        result = await agent.ainvoke({
            "raw_input": raw_input,
            "input_type": input_type,
            "related_memories": [],
            "messages": [],
        })
        # 将结果写回数据库
        await _save_result(share_id, result["analysis_result"])
    
    asyncio.run(_run())
```

---

### 4.7 配置管理 (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # ===== 应用 =====
    APP_NAME: str = "Share Helper"
    APP_ENV: str = "development"       # development / staging / production
    DEBUG: bool = True
    
    # ===== 数据库 =====
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/sharehelper"
    
    # ===== Redis =====
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # ===== LLM - 云端 =====
    CLOUD_LLM_BASE_URL: str = "https://api.openai.com/v1"
    CLOUD_LLM_API_KEY: str = ""
    CLOUD_LLM_MODEL: str = "gpt-4o"
    
    # ===== LLM - 本地 =====
    LOCAL_LLM_ENABLED: bool = False
    LOCAL_LLM_BASE_URL: str = "http://localhost:8000/v1"
    LOCAL_LLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct-AWQ"
    
    # ===== 向量数据库 =====
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "share_memories"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    MEMORY_SIMILARITY_THRESHOLD: float = 0.85
    
    # ===== 安全 =====
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

---

## 5. 系统架构总览图

```mermaid
graph TB
    subgraph "客户端"
        WEB["Web UI<br/>(Vite + Vue/React)"]
        MP["微信小程序<br/>(Phase 3)"]
    end

    subgraph "接入层"
        GW["FastAPI Gateway<br/>认证 / 限流 / 路由"]
        WS["WebSocket Server<br/>实时进度推送"]
    end

    subgraph "任务调度层"
        MQ["Redis / Celery<br/>异步任务队列"]
    end

    subgraph "智能体引擎层"
        AG["LangGraph Agent<br/>StateGraph 工作流"]
        CL["Input Classifier"]
        TE["Tool Executor"]
        MR["Memory Retriever"]
        AN["Analyzer"]
        AG --> CL --> TE --> MR --> AN
    end

    subgraph "工具层 (Parsers)"
        ZH["ZhihuParser"]
        BL["BilibiliParser"]
        DY["DouyinParser"]
        WC["WeChatArticleParser"]
        OCR["ImageOCR"]
        GS["GenericScraper"]
    end

    subgraph "LLM 层"
        CLOUD["云端 API<br/>(GPT-4o / 通义 / GLM)"]
        LOCAL["本地 vLLM<br/>(Qwen2.5 / Llama3)"]
    end

    subgraph "存储层"
        PG["PostgreSQL<br/>用户 / 分享 / 提醒"]
        QD["Qdrant<br/>向量记忆"]
        RD["Redis<br/>缓存 / 会话"]
    end

    WEB --> GW
    MP -.-> GW
    GW --> MQ
    GW <--> WS
    MQ --> AG
    TE --> ZH & BL & DY & WC & OCR & GS
    CL --> CLOUD
    AN --> CLOUD
    AN -.->|敏感内容| LOCAL
    MR --> QD
    AG --> PG
    GW --> RD
```

---

## 6. 数据流时序

```mermaid
sequenceDiagram
    participant U as 用户 (Web UI)
    participant G as FastAPI Gateway
    participant Q as Celery + Redis
    participant A as LangGraph Agent
    participant P as Parser Tool
    participant L as LLM (云端/本地)
    participant V as Qdrant 向量库
    participant D as PostgreSQL

    U->>G: POST /api/v1/shares {url: "https://bilibili.com/..."}
    G->>D: 创建 Share 记录 (status=PENDING)
    G->>Q: 派发 process_share 任务
    G-->>U: 202 Accepted {task_id: "xxx"}
    
    Q->>A: 启动 Agent 工作流
    A->>L: 1️⃣ 分类输入类型 → "bilibili"
    A->>P: 2️⃣ 调用 BilibiliParser
    P-->>A: ParseResult {title, content, duration}
    A->>V: 3️⃣ 向量检索相关历史分享 (Top-K)
    V-->>A: related_memories
    A->>L: 4️⃣ 综合分析 (内容 + 记忆 → 结构化报告)
    L-->>A: AnalysisResult JSON
    
    A->>D: 更新 Share (status=COMPLETED, 写入分析结果)
    A->>V: 存储当前内容向量
    A-->>G: WebSocket 推送完成事件
    G-->>U: WS event: {status: "completed", result: {...}}
```

---

## 7. Docker Compose 开发环境

```yaml
# docker-compose.yml
version: "3.9"
services:
  app:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres, redis, qdrant]
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes: ["./app:/code/app"]

  celery-worker:
    build: .
    env_file: .env
    depends_on: [postgres, redis]
    command: celery -A app.tasks.celery_app worker --loglevel=info -c 4

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: sharehelper
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: ["qdrant_data:/qdrant/storage"]

volumes:
  pgdata:
  qdrant_data:
```

---

## 8. 关键设计决策说明

### 8.1 为何先用 Celery 而非纯 FastAPI BackgroundTasks？

> FastAPI 的 `BackgroundTasks` 运行在同一进程的事件循环中。当 Parser 需要 Playwright 无头浏览器操作、vLLM 推理延迟高达数十秒时，会阻塞主进程的请求处理能力。**Celery Worker 独立进程**可隔离 CPU/内存，且天然支持重试、超时、限流，为 Phase 2 的分布式部署打好基础。

### 8.2 Agent 工具的注册机制

采用**注册表模式** (Registry Pattern)，新增平台只需：
1. 在 `app/tools/` 下新建 `xxx.py`，实现 `BaseParseTool`
2. 在 `app/tools/__init__.py` 的 `TOOL_REGISTRY` 中注册

Agent 的 `tool_executor` 节点根据 `detected_platform` 自动路由到对应工具，**零改动核心图逻辑**。

### 8.3 向量记忆的 MVP 策略

Phase 1 使用 Qdrant 的 **内存模式** (`":memory:"`)，不需要独立部署向量数据库即可跑通记忆关联流程。Phase 3 切换至持久化模式只需修改配置。

---

## 9. 实施路线图

### Phase 1 — MVP (预估 2-3 周)

| 周次 | 目标 | 具体产出 |
|-----|------|---------|
| Week 1 | 基础骨架 | 项目初始化、FastAPI 路由、DB 模型、Celery 配置、docker-compose |
| Week 2 | Agent 核心 | LangGraph 工作流、2-3 个 Parser (B站+知乎+通用)、LLM 集成 |
| Week 3 | 端到端联调 | Web UI (简单表单 + 结果展示)、WebSocket 实时推送、基础记忆功能 |

### Phase 2 — 分布式改造 (预估 2-3 周)

- vLLM 本地模型部署与 `PrivacyRouter` 联通
- Celery Worker 水平扩展测试
- Dockerfile + K8s YAML 编写
- 添加抖音、微信公众号 Parser

### Phase 3 — 多端 & 记忆深化 (预估 3-4 周)

- Qdrant 持久化部署 & 记忆合并算法优化
- APScheduler 提醒推送 + 微信/邮件通知
- 微信小程序端开发

---

## User Review Required

> [!IMPORTANT]
> 关键设计决策：

1. **技术栈确认**：ORM 选用 SQLAlchemy 2.0 (async)，包管理使用 `uv`
2. **前端框架**：MVP 阶段的 Web UI 使用 Vite + Vue 3
3. **项目命名**：代码包名使用 `app/`，项目根目录维持 `shareconn/`，
4. **MVP 范围确认**：Phase 1 先实现 B站 + 微信公众号 + 通用网页 三个 Parser
5. **现在就开始编码实现**

## Verification Plan

### Automated Tests
- `pytest` 单元测试覆盖 Agent 节点、Parser 工具、API 端点
- `pytest-asyncio` 异步测试
- `docker-compose up` 一键启动验证全链路

### Manual Verification
- 通过 Web UI 提交 B 站 / 知乎链接，验证完整解析流程
- 检查 PostgreSQL 数据写入
- 验证 WebSocket 实时推送
