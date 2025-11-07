# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 包概述

这是 ValueCell 的核心 Python 包,实现多智能体金融应用平台的核心编程模型。包含智能体框架、编排器、类型系统和服务器组件。

**核心职责**:
- 多智能体协调和编排 (Orchestrator)
- 异步流式响应管道 (ResponseRouter/ResponseBuffer)
- 智能体生命周期管理 (@agent 装饰器)
- Agent-to-Agent (A2A) 协议集成
- 对话持久化和记忆 (ConversationStore)

## 核心架构

### 多智能体协调流程

```
UserInput
  ↓
AgentOrchestrator.process_user_input()
  ├─ 后台生产者任务 (独立于客户端连接)
  └─ 消费者队列 (流式输出到 UI)
       ↓
SuperAgentService.triage()
  ├─ ANSWER: 直接回答 → yield StreamResponse
  └─ HANDOFF: enriched_query → PlanService
       ↓
PlanService.plan()
  ├─ UserInputRequest (HITL) → ExecutionContext (暂停状态)
  └─ ExecutionPlan → TaskExecutor
       ↓
TaskExecutor.execute_plan()
  └─ A2A Task → Remote Agent (via a2a-sdk)
       ↓
TaskStatusUpdateEvent / TaskArtifactUpdateEvent
  ↓
ResponseRouter.route() → BaseResponse
  ↓
ResponseBuffer.add() → 聚合 + annotate (item_id)
  ↓
ConversationStore.append() → SQLite + LanceDB
  ↓
yield BaseResponse → UI (SSE)
```

### 目录结构和职责

```
valuecell/
├── __init__.py                # 包入口,早期加载 .env 文件
│
├── core/                      # 核心编程模型
│   ├── types.py               # 类型系统 (UserInput, BaseResponse, Events)
│   ├── constants.py           # 全局常量
│   │
│   ├── agent/                 # Agent 装饰器和工具
│   │   ├── decorator.py       # @agent 装饰器 (添加 A2A 服务能力)
│   │   ├── card.py            # Agent Card 管理 (从 YAML 加载)
│   │   ├── connect.py         # Agent 连接和注册
│   │   └── responses.py       # 响应事件断言和过滤
│   │
│   ├── coordinate/            # 编排器
│   │   ├── orchestrator.py    # AgentOrchestrator (协调所有流程)
│   │   └── services.py        # AgentServiceBundle (依赖注入)
│   │
│   ├── super_agent/           # SuperAgent 快速分类
│   │   ├── service.py         # SuperAgentService (ANSWER/HANDOFF 决策)
│   │   └── types.py           # SuperAgentDecision, SuperAgentOutcome
│   │
│   ├── plan/                  # Planner 规划器
│   │   ├── planner.py         # PlanService (生成执行计划, 支持 HITL)
│   │   └── types.py           # ExecutionPlan, UserInputRequest
│   │
│   ├── task/                  # 任务执行
│   │   ├── executor.py        # TaskExecutor (执行计划中的任务)
│   │   └── types.py           # TaskDefinition, TaskResult
│   │
│   ├── event/                 # 事件响应处理
│   │   ├── router.py          # ResponseRouter (A2A Event → BaseResponse)
│   │   ├── buffer.py          # ResponseBuffer (缓存、聚合、持久化)
│   │   └── service.py         # EventResponseService (事件映射和路由)
│   │
│   └── conversation/          # 对话管理
│       ├── service.py         # ConversationService (对话生命周期)
│       ├── store.py           # ConversationStore (SQLite + LanceDB)
│       └── types.py           # Conversation, ConversationStatus
│
├── agents/                    # 智能体实现
│   ├── __init__.py
│   ├── research_agent.py      # ResearchAgent (财务文档研究)
│   ├── auto_trading_agent.py  # AutoTradingAgent (自动交易)
│   └── news_agent.py          # NewsAgent (新闻推送)
│
├── server/                    # FastAPI 后端
│   ├── main.py                # 服务入口 (uvicorn)
│   ├── api/                   # REST API
│   │   ├── app.py             # FastAPI 应用工厂
│   │   ├── routers/           # API 路由器
│   │   ├── schemas.py         # Pydantic 请求/响应模型
│   │   └── exceptions.py      # 异常处理器
│   ├── config/
│   │   └── settings.py        # Settings (三层配置系统)
│   ├── db/
│   │   ├── models.py          # SQLAlchemy 模型
│   │   └── init_db.py         # 数据库初始化
│   └── services/              # 业务逻辑服务
│       └── orchestrator_service.py
│
├── adapters/                  # 外部数据适配器
│   ├── models/                # 数据源适配器 (yfinance, akshare)
│   └── assets/                # 资产数据管理器
│
├── configs/                   # YAML 配置
│   ├── config.yaml            # 全局配置
│   ├── providers/             # LLM 提供商配置
│   ├── agents/                # 智能体配置
│   ├── agent_cards/           # Agent Card 定义
│   └── locales/               # 国际化配置
│
└── utils/                     # 工具函数
    ├── uuid.py                # UUID 生成 (item_id, task_id, thread_id)
    ├── logger.py              # Loguru 配置
    └── ...
```

## 核心类型系统

### 用户输入 (core/types.py)

```python
class UserInput(BaseModel):
    query: str                              # 用户输入文本
    target_agent_name: Optional[str]        # 目标智能体名称
    meta: UserInputMetadata                 # 元数据 (conversation_id, user_id)
```

### 响应类型 (core/types.py)

所有智能体必须 yield 以下类型之一:

1. **StreamResponse**: 流式响应 (消息块、工具调用、推理)
   ```python
   StreamResponse(
       content="Processing...",
       event=StreamResponseEvent.MESSAGE_CHUNK,  # 或 TOOL_CALL_STARTED, REASONING, etc.
       metadata={"progress": 0.5}
   )
   ```

2. **NotifyResponse**: 通知响应 (定时推送、事件通知)
   ```python
   NotifyResponse(
       content="Market alert: AAPL +5%",
       event=NotifyResponseEvent.MESSAGE
   )
   ```

3. **ComponentResponse**: UI 组件响应 (图表、报告、配置面板)
   ```python
   # 通过 metadata 传递 component_id 来支持组件替换
   StreamResponse(
       content=json.dumps(report_data),
       event=CommonResponseEvent.COMPONENT_GENERATOR,
       metadata={"component_id": "report_123", "component_type": ComponentType.REPORT}
   )
   ```

### 事件枚举 (core/types.py)

- **SystemResponseEvent**: `CONVERSATION_STARTED`, `THREAD_STARTED`, `PLAN_REQUIRE_USER_INPUT`, `DONE`
- **TaskStatusEvent**: `TASK_STARTED`, `TASK_COMPLETED`, `TASK_FAILED`, `TASK_CANCELLED`
- **StreamResponseEvent**: `MESSAGE_CHUNK`, `TOOL_CALL_STARTED`, `REASONING`, `REASONING_COMPLETED`
- **NotifyResponseEvent**: `MESSAGE`
- **CommonResponseEvent**: `COMPONENT_GENERATOR`

### BaseResponse 类型层次 (core/types.py)

```
BaseResponse (抽象基类)
├── StreamResponse (流式响应)
├── NotifyResponse (通知响应)
└── SystemResponse (系统级响应)
    ├── ConversationStarted
    ├── ThreadStarted
    ├── PlanRequireUserInput
    └── Done
```

## 核心组件详解

### 1. AgentOrchestrator (core/coordinate/orchestrator.py)

**职责**: 协调整个多智能体系统的执行流程

**关键特性**:
- **后台生产者模式**: `process_user_input()` 创建独立的后台任务,与客户端连接解耦
- **ExecutionContext**: 管理 HITL 暂停/恢复状态,支持超时和用户验证
- **异步队列**: 生产者通过队列向消费者传递响应,支持断线重连

**核心方法**:
```python
async def process_user_input(user_input: UserInput) -> AsyncGenerator[BaseResponse, None]:
    """流式处理用户输入,后台任务独立运行"""

async def provide_user_feedback(conversation_id: str, user_id: str, feedback: str) -> ...:
    """提供 HITL 反馈,恢复暂停的执行"""
```

**状态管理**:
- `_execution_contexts: Dict[str, ExecutionContext]` - 跟踪暂停的执行
- ExecutionContext 支持过期检查 (默认 1 小时)

### 2. SuperAgentService (core/super_agent/service.py)

**职责**: 快速判断用户意图,决定直接回答还是转交规划

**决策类型** (SuperAgentDecision):
- `ANSWER`: 直接回答用户查询 (简单问题、闲聊)
- `HANDOFF`: 转交给 Planner (复杂任务、需要多步骤执行)

**核心方法**:
```python
async def triage(user_input: UserInput) -> AsyncGenerator[SuperAgentOutcome, None]:
    """
    分类用户输入并可选地充实上下文

    Returns:
        SuperAgentOutcome:
            - decision: ANSWER | HANDOFF
            - enriched_query: 充实后的查询 (用于 HANDOFF)
            - response_generator: 直接回答生成器 (用于 ANSWER)
    """
```

### 3. PlanService (core/plan/planner.py)

**职责**: 根据用户意图生成执行计划,支持 HITL 交互

**核心概念**:
- **UserInputRequest**: 当缺少信息或需要确认时发出,暂停执行
- **ExecutionPlan**: 包含多个 TaskDefinition 的执行计划
- **HITL 循环**: 可多次请求用户输入,直到生成充分的计划

**核心方法**:
```python
async def plan(enriched_query: str, user_input: UserInput) -> AsyncGenerator[...]:
    """
    生成执行计划,支持 HITL

    Yields:
        - UserInputRequest (如果需要用户输入)
        - ExecutionPlan (最终生成的计划)
    """
```

### 4. TaskExecutor (core/task/executor.py)

**职责**: 执行计划中的任务,调用远程智能体

**执行模式**:
- **同步执行**: 按顺序执行任务列表
- **A2A 调用**: 通过 `a2a-sdk` 发送任务到远程智能体
- **事件路由**: 接收 TaskStatusUpdateEvent 并路由到 EventResponseService

**核心方法**:
```python
async def execute_plan(plan: ExecutionPlan) -> AsyncGenerator[BaseResponse, None]:
    """执行计划中的所有任务,流式返回响应"""
```

### 5. ResponseRouter & ResponseBuffer (core/event/)

**ResponseRouter 职责**: 将 A2A 事件转换为统一的 BaseResponse

**映射规则**:
- `TaskStatusUpdateEvent` → 根据 status 映射到 TaskStatusEvent
- `TaskArtifactUpdateEvent` → 根据 artifact 类型映射到 StreamResponse/NotifyResponse

**ResponseBuffer 职责**: 缓存、聚合和持久化响应

**关键特性**:
- **稳定 ID**: 为每个响应生成 `item_id`,支持部分聚合
- **组件替换**: 通过 `component_id` 支持前端组件替换 (而不是追加)
- **自动持久化**: 调用 ConversationStore.append() 保存到数据库

**核心方法**:
```python
# ResponseRouter
async def route(event: TaskStatusUpdateEvent | TaskArtifactUpdateEvent) -> BaseResponse:
    """将 A2A 事件路由到 BaseResponse"""

# ResponseBuffer
async def add(response: BaseResponse, conversation_id: str, thread_id: str) -> BaseResponse:
    """添加响应到缓存,生成 item_id,并持久化"""
```

### 6. ConversationStore (core/conversation/store.py)

**职责**: 持久化对话历史和向量知识库

**存储后端**:
- **SQLite**: 结构化对话数据 (会话、消息、元数据)
- **LanceDB**: 向量知识库 (语义搜索、上下文检索)

**核心方法**:
```python
async def append(conversation_id: str, thread_id: str, item: BaseResponse):
    """追加响应到对话历史"""

async def get_conversation_history(conversation_id: str) -> List[BaseResponse]:
    """获取完整对话历史"""
```

## @agent 装饰器 (core/agent/decorator.py)

**职责**: 为智能体类添加 A2A 服务器能力

**使用方式**:
```python
from valuecell.core.agent import agent

@agent
class MyAgent:
    async def run(self, query: str) -> AsyncGenerator[BaseResponse, None]:
        yield StreamResponse(
            content="Processing...",
            event=StreamResponseEvent.MESSAGE_CHUNK
        )
```

**装饰器功能**:
1. 加载 Agent Card (从 `configs/agent_cards/{agent_name}.yaml`)
2. 创建 A2A Server (AgentExecutor + A2AStarletteApplication)
3. 添加 `serve()` 方法 (启动 uvicorn 服务器)
4. 注册到 AgentRegistry (可选)

**Agent Card 结构** (configs/agent_cards/\*.yaml):
```yaml
name: my_agent
display_name: My Agent
description: A brief description
version: 1.0.0
url: http://0.0.0.0:8081
capabilities:
  - research
  - analysis
```

## 智能体开发模式

### 1. 基础智能体 (同步流式)

```python
from valuecell.core.agent import agent
from valuecell.core.types import StreamResponse, StreamResponseEvent

@agent
class BasicAgent:
    async def run(self, query: str):
        # 工具调用开始
        yield StreamResponse(
            content=None,
            event=StreamResponseEvent.TOOL_CALL_STARTED,
            metadata={"tool_name": "search", "tool_call_id": "call_123"}
        )

        # 执行工具
        result = await self.search(query)

        # 工具调用完成
        yield StreamResponse(
            content=result,
            event=StreamResponseEvent.TOOL_CALL_COMPLETED,
            metadata={"tool_call_id": "call_123"}
        )

        # 流式输出消息
        for chunk in self.generate_response(result):
            yield StreamResponse(
                content=chunk,
                event=StreamResponseEvent.MESSAGE_CHUNK
            )
```

### 2. 推理智能体 (带推理过程)

```python
@agent
class ReasoningAgent:
    async def run(self, query: str):
        # 推理开始
        yield StreamResponse(
            content=None,
            event=StreamResponseEvent.REASONING_STARTED
        )

        # 流式推理过程
        for thought in self.reasoning_chain(query):
            yield StreamResponse(
                content=thought,
                event=StreamResponseEvent.REASONING
            )

        # 推理完成
        yield StreamResponse(
            content=None,
            event=StreamResponseEvent.REASONING_COMPLETED
        )

        # 输出最终答案
        yield StreamResponse(
            content=self.final_answer,
            event=StreamResponseEvent.MESSAGE_CHUNK
        )
```

### 3. 组件生成智能体 (UI 组件)

```python
from valuecell.core.types import CommonResponseEvent, ComponentType

@agent
class ReportAgent:
    async def run(self, query: str):
        # 生成报告数据
        report_data = await self.generate_report(query)

        # 发送报告组件 (component_id 支持替换而不是追加)
        yield StreamResponse(
            content=json.dumps({
                "title": "Financial Report",
                "data": report_data,
                "create_time": "2025-01-15 10:30:00"
            }),
            event=CommonResponseEvent.COMPONENT_GENERATOR,
            metadata={
                "component_id": f"report_{query_hash}",  # 相同 ID 会替换旧组件
                "component_type": ComponentType.REPORT
            }
        )
```

### 4. 定时推送智能体 (后台任务)

```python
from valuecell.core.types import NotifyResponse, NotifyResponseEvent
import asyncio

@agent
class NewsAgent:
    async def run(self, query: str):
        # 解析定时配置
        schedule = self.parse_schedule(query)

        # 返回任务控制器组件
        yield StreamResponse(
            content=json.dumps({"task_id": "news_123", "schedule": schedule}),
            event=CommonResponseEvent.COMPONENT_GENERATOR,
            metadata={"component_type": ComponentType.SCHEDULED_TASK_CONTROLLER}
        )

        # 后台定时任务 (独立于客户端连接)
        while True:
            await asyncio.sleep(schedule.interval)

            news = await self.fetch_news()

            # 推送通知
            yield NotifyResponse(
                content=news,
                event=NotifyResponseEvent.MESSAGE
            )
```

## 异步和可重入设计

### 后台生产者模式

**问题**: 客户端 SSE 连接可能断开,但长时间任务需要继续执行

**解决方案**: AgentOrchestrator 使用后台生产者任务 + 队列

```python
async def process_user_input(user_input: UserInput):
    queue = asyncio.Queue()
    active = {"value": True}

    async def emit(item):
        if active["value"]:
            await queue.put(item)

    # 后台任务,独立运行
    asyncio.create_task(self._run_session(user_input, emit))

    try:
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item
    except asyncio.CancelledError:
        active["value"] = False  # 标记为非活跃,但不取消后台任务
        raise
```

**好处**:
- 定时任务可以在客户端断开后继续运行
- 支持多客户端订阅同一对话
- 状态持久化到 ConversationStore,支持恢复

### HITL (人在回路) 可重入

**流程**:
1. Planner 发现缺少信息 → yield `UserInputRequest`
2. Orchestrator 创建 `ExecutionContext`,保存状态
3. 客户端收到 `PLAN_REQUIRE_USER_INPUT` 事件
4. 用户提供反馈 → `provide_user_feedback()`
5. Orchestrator 恢复 `ExecutionContext`,继续规划

**ExecutionContext 管理**:
```python
class ExecutionContext:
    stage: str              # "planning" | "execution"
    conversation_id: str
    thread_id: str
    user_id: str
    created_at: float       # 用于过期检查
    metadata: Dict          # 保存中间状态

    def is_expired(self, max_age_seconds=3600) -> bool:
        """检查是否超时 (默认 1 小时)"""

    def validate_user(self, user_id: str) -> bool:
        """验证用户身份"""
```

## A2A (Agent-to-Agent) 协议

### 消息流

```
Orchestrator → TaskExecutor
  ↓
  send_message(Task) → Remote Agent (via HTTP)
  ↓
Remote Agent 处理 Task
  ↓
  TaskStatusUpdateEvent (RUNNING, COMPLETED, FAILED)
  TaskArtifactUpdateEvent (消息块、工具调用、推理)
  ↓
ResponseRouter → BaseResponse
  ↓
ResponseBuffer → ConversationStore → UI
```

### 启动 A2A Agent

```python
@agent
class MyAgent:
    async def run(self, query: str):
        # 智能体逻辑
        pass

# 启动 A2A 服务器
async def main():
    agent = MyAgent()
    await agent.serve()  # 由 @agent 装饰器添加

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 配置系统

### 三层配置 (优先级: 环境变量 > .env > YAML)

**加载顺序** (在 `__init__.py` 中):
1. `load_env_file_early()` - 包导入时立即加载 .env
2. `Settings.from_yaml()` - 从 YAML 读取默认值
3. `os.getenv()` - 环境变量覆盖

**配置文件**:
- `configs/config.yaml` - 全局配置
- `configs/providers/*.yaml` - LLM 提供商
- `configs/agents/*.yaml` - 智能体配置
- `configs/agent_cards/*.yaml` - Agent Card 定义

**读取配置**:
```python
from valuecell.server.config.settings import get_settings

settings = get_settings()  # 单例,缓存配置
print(settings.API_HOST, settings.API_PORT)
```

## 类型安全和验证

### Pydantic 模型

**所有数据结构都使用 Pydantic**:
- 自动类型验证
- JSON 序列化/反序列化
- 清晰的错误消息

**示例**:
```python
from pydantic import BaseModel, Field

class MyRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query")
    options: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"  # 禁止额外字段
```

### 避免裸 dict

**不推荐**:
```python
def process(data: dict) -> dict:  # 类型不明确
    return {"result": data["query"]}
```

**推荐**:
```python
def process(request: MyRequest) -> MyResponse:  # 强类型
    return MyResponse(result=request.query)
```

## 性能优化

### 异步并发

```python
import asyncio

# 并发调用多个智能体
results = await asyncio.gather(
    agent1.run(query),
    agent2.run(query),
    agent3.run(query)
)
```

### 流式传输

```python
# 避免内存积累,逐块传输
async def stream_large_data():
    for chunk in generate_chunks():
        yield StreamResponse(
            content=chunk,
            event=StreamResponseEvent.MESSAGE_CHUNK
        )
```

### ResponseBuffer 聚合

ResponseBuffer 支持部分聚合,减少 DB 写入:
- 消息块自动合并 (相同 item_id)
- 工具调用结果更新 (而不是追加)
- 组件替换 (通过 component_id)

## 常见模式

### 1. 错误处理

```python
from valuecell.core.types import TaskStatusEvent

async def run(self, query: str):
    try:
        result = await self.process(query)
        yield StreamResponse(
            content=result,
            event=StreamResponseEvent.MESSAGE_CHUNK
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        yield StreamResponse(
            content=f"Error: {str(e)}",
            event=TaskStatusEvent.TASK_FAILED
        )
```

### 2. 进度报告

```python
async def run(self, query: str):
    steps = ["step1", "step2", "step3"]

    for i, step in enumerate(steps):
        # 报告进度
        yield StreamResponse(
            content=f"Processing {step}...",
            event=StreamResponseEvent.MESSAGE_CHUNK,
            metadata={"progress": (i + 1) / len(steps)}
        )

        await self.execute_step(step)
```

### 3. 工具调用追踪

```python
async def run(self, query: str):
    tool_call_id = generate_uuid()

    # 开始
    yield StreamResponse(
        content=None,
        event=StreamResponseEvent.TOOL_CALL_STARTED,
        metadata={"tool_name": "search", "tool_call_id": tool_call_id}
    )

    # 执行
    result = await self.search_tool(query)

    # 完成
    yield StreamResponse(
        content=result,
        event=StreamResponseEvent.TOOL_CALL_COMPLETED,
        metadata={"tool_call_id": tool_call_id}
    )
```

## 调试技巧

### 启用详细日志

```python
import logging
from loguru import logger

# 设置日志级别
logger.add("debug.log", level="DEBUG")
logger.debug("Processing query", query=user_input.query)
```

### 追踪响应流

```python
# 在 ResponseBuffer 中添加日志
async def add(self, response: BaseResponse, ...):
    logger.info(f"Adding response: {response.event}", item_id=item_id)
    # ...
```

### 检查 ExecutionContext

```python
# 在 Orchestrator 中
logger.info(f"Active contexts: {list(self._execution_contexts.keys())}")
for ctx_id, ctx in self._execution_contexts.items():
    logger.info(f"Context {ctx_id}: stage={ctx.stage}, expired={ctx.is_expired()}")
```

## 架构原则

### 1. 单一职责
- 每个类/模块只负责一件事
- Orchestrator 协调,不实现业务逻辑
- SuperAgent 分类,不执行任务

### 2. 依赖注入
- 使用 AgentServiceBundle 组合服务
- 支持 Mock 服务用于测试

### 3. 位置透明
- 智能体可以是本地或远程
- A2A 协议统一通信接口

### 4. 异步优先
- 所有 I/O 操作都是 async
- 支持并发和流式传输

### 5. 类型安全
- 充分使用 Pydantic 模型
- 避免裸 dict 和 any 类型

## 扩展点

### 添加新的响应类型

1. 在 `core/types.py` 定义新的 Event Enum
2. 在 `ResponseRouter` 添加映射规则
3. 在前端添加相应的处理逻辑

### 添加新的存储后端

1. 实现 `ConversationStore` 接口
2. 在 `AgentServiceBundle` 中注入
3. 更新配置以支持新后端

### 添加新的 Planner 策略

1. 继承 `PlanService` 基类
2. 实现 `plan()` 方法
3. 在 Orchestrator 中切换使用

## 参考资源

- **agno 文档**: https://github.com/agno-ai/agno
- **a2a-sdk 文档**: https://github.com/a2a-protocol/a2a-sdk
- **Pydantic 文档**: https://docs.pydantic.dev/
- **FastAPI 文档**: https://fastapi.tiangolo.com/
