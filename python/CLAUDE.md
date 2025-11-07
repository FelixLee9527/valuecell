# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是 ValueCell 的 Python 后端包,提供多智能体金融应用平台的核心编程模型、智能体实现和 FastAPI 服务器。

**技术栈**:
- Python 3.12+
- FastAPI + Uvicorn (Web 服务器)
- SQLAlchemy + aiosqlite (数据库)
- Pydantic (数据验证)
- agno v2.0 (智能体框架)
- a2a-sdk (智能体间通信)
- loguru (结构化日志)

## 常用命令

### 依赖管理

```bash
# 同步所有依赖组
uv sync --group dev        # 开发依赖 (包含 lint, style, test)
uv sync --group test       # 仅测试依赖
uv sync --group lint       # 仅 lint 依赖

# 添加新依赖
uv add package-name                    # 生产依赖
uv add --dev package-name              # 开发依赖
uv add --group test package-name       # 测试依赖

# 升级依赖
uv sync --upgrade          # 升级所有依赖
uv add package-name --upgrade  # 升级特定包

# 查看依赖
uv pip list                # 列出所有已安装的包
uv tree                    # 显示依赖树
```

**重要**: 永远使用 `uv`,禁止使用 `pip`, `poetry`, `conda`, `python3`, `python` 命令。

### 启动服务

```bash
# 启动 FastAPI 后端服务器
uv run --env-file ../.env valuecell/server/main.py

# 使用 uvicorn 直接启动 (带热重载)
uv run uvicorn valuecell.server.main:app --reload --host 0.0.0.0 --port 8000

# 交互式智能体启动器
uv run --with questionary scripts/launch.py

# 启动特定智能体
uv run --env-file ../.env -m valuecell.agents.research_agent
uv run --env-file ../.env -m valuecell.agents.auto_trading_agent
uv run --env-file ../.env -m valuecell.agents.news_agent

# 初始化数据库
uv run valuecell/server/db/init_db.py
```

### 代码质量检查

```bash
# Ruff 代码检查和格式化
ruff check .               # 检查代码质量问题
ruff check . --fix         # 自动修复可修复的问题
ruff format .              # 格式化代码
ruff format . --check      # 仅检查格式,不修改

# isort 导入排序
isort .                    # 排序所有导入
isort . --check-only       # 仅检查导入顺序

# 组合检查
ruff check . && ruff format . && isort .
```

**Ruff 配置** (pyproject.toml):
- 行长度: 88 字符
- 缩进: 4 空格
- 目标版本: Python 3.12
- 引号风格: 双引号
- 排除目录: venv, build, dist, node_modules, third_party

### 测试

```bash
# 运行所有测试
pytest

# 带覆盖率
pytest --cov                           # 显示覆盖率报告
pytest --cov --cov-report=html         # 生成 HTML 覆盖率报告
pytest --cov --cov-report=xml          # 生成 XML 覆盖率报告 (用于 CI)
diff-cover coverage.xml                # 检查代码变更的覆盖率

# 运行特定测试
pytest path/to/test_file.py            # 运行单个文件
pytest path/to/test_file.py::test_name # 运行特定测试函数
pytest -k "pattern"                    # 运行匹配模式的测试
pytest -m "mark"                       # 运行带特定标记的测试

# 详细输出
pytest -v                              # 详细模式
pytest -vv                             # 更详细
pytest -s                              # 显示 print 输出
pytest --tb=short                      # 简短的错误回溯
pytest --tb=long                       # 详细的错误回溯

# 异步测试
pytest -v --asyncio-mode=auto          # 自动检测异步测试

# 失败时立即停止
pytest -x                              # 第一个失败后停止
pytest --maxfail=3                     # 3 个失败后停止

# 重新运行失败的测试
pytest --lf                            # 仅运行上次失败的测试
pytest --ff                            # 先运行失败的,再运行其他的
```

**测试排除目录**: .venv, venv, build, dist, logs, third_party, examples, docs

### 环境变量

```bash
# 验证环境变量加载
uv run python -c "from valuecell.server.config.settings import get_settings; s = get_settings(); print(f'API: {s.API_HOST}:{s.API_PORT}')"

# 检查 LLM 配置
uv run python -c "from valuecell.server.config.settings import get_settings; import os; print('OPENROUTER_API_KEY:', 'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET')"
```

## 核心架构

### 目录结构

```
python/
├── valuecell/
│   ├── __init__.py           # 包入口,版本定义
│   │
│   ├── core/                 # 核心编程模型
│   │   ├── agent/            # Agent 装饰器、连接、Agent Card
│   │   ├── coordinate/       # Orchestrator 编排器
│   │   ├── super_agent/      # SuperAgent 快速分类
│   │   ├── plan/             # Planner 规划器 (支持 HITL)
│   │   ├── task/             # TaskExecutor 任务执行
│   │   ├── event/            # ResponseRouter/ResponseBuffer 事件处理
│   │   ├── conversation/     # ConversationStore 对话记忆
│   │   ├── types.py          # 核心类型定义
│   │   └── constants.py      # 常量定义
│   │
│   ├── agents/               # 智能体实现
│   │   ├── research_agent.py       # 研究智能体
│   │   ├── auto_trading_agent.py   # 自动交易智能体
│   │   ├── news_agent.py           # 新闻推送智能体
│   │   └── __init__.py
│   │
│   ├── server/               # FastAPI 后端服务
│   │   ├── main.py           # 服务入口 (uvicorn)
│   │   ├── api/              # REST API
│   │   │   ├── app.py        # FastAPI 应用工厂
│   │   │   ├── routers/      # API 路由
│   │   │   │   ├── agent.py
│   │   │   │   ├── agent_stream.py
│   │   │   │   ├── conversation.py
│   │   │   │   ├── task.py
│   │   │   │   └── ...
│   │   │   ├── schemas.py    # Pydantic 模型
│   │   │   └── exceptions.py # 异常处理
│   │   ├── config/           # 配置管理
│   │   │   └── settings.py   # Settings (三层配置)
│   │   ├── db/               # 数据库
│   │   │   ├── models.py     # SQLAlchemy 模型
│   │   │   └── init_db.py    # 数据库初始化
│   │   └── services/         # 业务逻辑服务
│   │       ├── orchestrator_service.py
│   │       └── ...
│   │
│   ├── adapters/             # 外部数据适配器
│   │   ├── models/           # 数据适配器
│   │   │   ├── yfinance_adapter.py
│   │   │   ├── akshare_adapter.py
│   │   │   └── ...
│   │   └── assets/           # 资产数据管理
│   │
│   ├── configs/              # YAML 配置文件
│   │   ├── config.yaml       # 全局配置
│   │   ├── providers/        # LLM 提供商配置
│   │   ├── agents/           # 智能体配置
│   │   ├── agent_cards/      # Agent Card 定义
│   │   └── locales/          # 国际化
│   │
│   └── utils/                # 工具函数
│       ├── uuid.py           # UUID 生成
│       ├── logger.py         # 日志配置
│       └── ...
│
├── scripts/
│   ├── launch.py             # 交互式智能体启动器
│   └── prepare_envs.sh       # 环境初始化
│
├── third_party/              # 第三方智能体
│   ├── ai-hedge-fund/        # AI 对冲基金智能体
│   └── TradingAgents/        # 交易分析智能体
│
├── pyproject.toml            # 项目配置和依赖
├── README.md                 # 包说明文档
└── .venv/                    # 虚拟环境 (不提交到 git)
```

### 核心模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| **Orchestrator** | `core/coordinate/orchestrator.py` | 协调整个流程,管理状态转移,支持 HITL 暂停/恢复 |
| **SuperAgent** | `core/super_agent/` | 快速判断是否需要规划,提供上下文充实 |
| **Planner** | `core/plan/planner.py` | 根据用户意图生成执行计划,支持 HITL 交互 |
| **TaskExecutor** | `core/task/executor.py` | 执行计划中的各个任务,调用远程智能体 |
| **ResponseRouter** | `core/event/router.py` | 将 A2A 事件转换为统一的 BaseResponse |
| **ResponseBuffer** | `core/event/buffer.py` | 响应缓存、聚合和持久化 |
| **ConversationStore** | `core/conversation/` | 对话历史持久化 (SQLite + LanceDB) |
| **AgentDecorator** | `core/agent/decorator.py` | `@agent` 装饰器,为智能体类添加 A2A 服务能力 |
| **AgentCard** | `core/agent/card.py` | 智能体元数据管理 (从 YAML 加载) |
| **Settings** | `server/config/settings.py` | 三层配置系统 (环境变量 > .env > YAML) |

### 多智能体协调流程

```
用户输入 (UserInput)
  ↓
Orchestrator.process_user_input()
  ↓
SuperAgentService.triage()
  ├→ ANSWER: 直接回答 → StreamResponse → ResponseBuffer → UI
  └→ HANDOFF: enriched_query → PlanService
       ↓
PlanService.plan()
  ├→ UserInputRequest (HITL) → 暂停,等待用户输入
  └→ ExecutionPlan → TaskExecutor
       ↓
TaskExecutor.execute_plan()
  └→ A2A Protocol → Remote Agents
       ↓
TaskStatusUpdateEvent / TaskArtifactUpdateEvent
  ↓
ResponseRouter.route() → BaseResponse (StreamResponse/NotifyResponse)
  ↓
ResponseBuffer.add() → 聚合、annotate、持久化
  ↓
ConversationStore.append() → SQLite + LanceDB
  ↓
Stream to UI (SSE)
```

### 异步和可重入设计

- **全异步**: 所有 I/O 操作都使用 `async`/`await`,支持并发
- **后台生产者**: 长时间运行的任务在后台执行,与客户端连接解耦
- **HITL 支持**: Planner 可暂停并等待用户输入,然后恢复执行
- **稳定 ID**: ResponseBuffer 使用稳定的 `item_id` 支持部分聚合
- **位置透明**: 智能体可以是本地或远程,通过 A2A 协议无缝切换

### Agent-to-Agent (A2A) 协议

- 使用 `a2a-sdk` 定义任务和消息模式
- 支持 HTTP 和其他传输方式
- 流式响应管道: A2A Events → ResponseRouter → ResponseBuffer → Store → UI
- 智能体装饰器 `@agent` 自动添加 A2A 服务器能力

## 智能体开发

### 添加新智能体

1. **创建智能体实现**: `valuecell/agents/{agent_name}.py`

```python
from valuecell.core.agent import agent
from valuecell.core.types import BaseResponse, StreamResponse, StreamResponseEvent

@agent
class MyNewAgent:
    """My new agent description."""

    async def run(self, query: str) -> AsyncGenerator[BaseResponse, None]:
        """Process user query and yield responses."""
        yield StreamResponse(
            content="Processing your request...",
            event=StreamResponseEvent.MESSAGE_CHUNK
        )
        # ... 智能体逻辑 ...
```

2. **定义 Agent Card**: `valuecell/configs/agent_cards/{agent_name}.yaml`

```yaml
name: my_new_agent
display_name: My New Agent
description: A brief description of what this agent does
version: 1.0.0
author: Your Name
categories:
  - research
  - analysis
capabilities:
  - task_type_1
  - task_type_2
```

3. **添加智能体配置**: `valuecell/configs/agents/{agent_name}.yaml`

```yaml
agent:
  name: my_new_agent
  host: "0.0.0.0"
  port: 8081

model:
  provider: openrouter
  name: anthropic/claude-3.5-sonnet
  temperature: 0.7
```

4. **注册智能体**: 在 `scripts/launch.py` 中添加启动命令

```python
MAP_NAME_COMMAND["MyNewAgent"] = (
    f"uv run --env-file {ENV_PATH_STR} -m valuecell.agents.my_new_agent"
)
```

5. **运行智能体**:

```bash
uv run --env-file ../.env -m valuecell.agents.my_new_agent
```

### 智能体类型

**已实现的智能体**:
- **SuperAgent**: 快速分类和上下文充实 (`core/super_agent/`)
- **ResearchAgent**: 基于财务文档的研究分析 (`agents/research_agent.py`)
- **AutoTradingAgent**: 基于技术指标的自动交易 (`agents/auto_trading_agent.py`)
- **NewsAgent**: 定时新闻推送 (`agents/news_agent.py`)

**第三方智能体** (在 `third_party/` 目录):
- **AI-HedgeFund Agents**: Warren Buffett, Charlie Munger, Peter Lynch 等投资风格
- **TradingAgents**: 市场分析、情感分析、基本面分析

### 响应类型

智能体可以 yield 以下响应类型 (定义在 `core/types.py`):

1. **StreamResponse**: 流式响应 (消息块、工具调用、推理过程)
   ```python
   StreamResponse(
       content="Processing...",
       event=StreamResponseEvent.MESSAGE_CHUNK,
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

3. **ComponentResponse**: UI 组件响应 (图表、表格等)
   ```python
   ComponentResponse(
       component_type="chart",
       props={"data": [...], "type": "line"}
   )
   ```

## 配置管理

### 三层配置系统 (优先级从高到低)

1. **环境变量** - 运行时覆盖,直接设置环境变量
2. **.env 文件** - 用户级配置,在项目根目录 `../.env`
3. **YAML 文件** - 系统默认值,在 `valuecell/configs/`

### 配置文件位置

- **全局配置**: `valuecell/configs/config.yaml`
- **LLM 提供商**: `valuecell/configs/providers/*.yaml`
- **智能体配置**: `valuecell/configs/agents/*.yaml`
- **Agent Cards**: `valuecell/configs/agent_cards/*.yaml`
- **国际化**: `valuecell/configs/locales/{lang}/*.yaml`

### 读取配置

```python
from valuecell.server.config.settings import get_settings

settings = get_settings()
print(f"API running on {settings.API_HOST}:{settings.API_PORT}")
```

## 数据库管理

### 数据存储

- **对话历史**: SQLite (`../valuecell.db`)
- **向量知识库**: LanceDB (`../.lancedb/`)
- **知识库缓存**: `../.knowledgebase/`

### 数据库操作

```bash
# 初始化数据库
uv run valuecell/server/db/init_db.py

# 检查数据库 (需要安装 sqlite3)
sqlite3 ../valuecell.db ".tables"
sqlite3 ../valuecell.db "SELECT * FROM conversations LIMIT 5;"
sqlite3 ../valuecell.db "SELECT COUNT(*) FROM conversations;"

# 重置数据库 (清除所有数据)
cd ..
rm -rf lancedb/ valuecell.db .knowledgebase/
cd python
uv run valuecell/server/db/init_db.py
```

### SQLAlchemy 模型

模型定义在 `valuecell/server/db/models.py`:
- `Conversation`: 对话记录
- `Message`: 消息记录
- `UserProfile`: 用户配置
- `Watchlist`: 监控列表

## API 开发

### 添加新的 API 端点

1. **定义 Pydantic Schema** (`server/api/schemas.py`):

```python
class MyRequest(BaseModel):
    query: str = Field(..., description="User query")
    options: Optional[dict] = None

class MyResponse(BaseModel):
    result: str
    metadata: Optional[dict] = None
```

2. **创建 Router** (`server/api/routers/my_router.py`):

```python
from fastapi import APIRouter, Depends
from ..schemas import MyRequest, MyResponse, SuccessResponse

def create_my_router() -> APIRouter:
    router = APIRouter(prefix="/api/my", tags=["my"])

    @router.post("/endpoint", response_model=SuccessResponse[MyResponse])
    async def my_endpoint(request: MyRequest):
        # 处理逻辑
        result = process(request.query)
        return SuccessResponse(
            data=MyResponse(result=result)
        )

    return router
```

3. **注册 Router** (`server/api/app.py`):

```python
from .routers.my_router import create_my_router

def create_app() -> FastAPI:
    app = FastAPI(...)
    app.include_router(create_my_router())
    return app
```

### 现有 API 端点

- `GET /` - 应用信息
- `GET /health` - 健康检查
- `POST /api/chat/send` - 发送消息给智能体
- `GET /api/chat/stream` - 流式接收智能体响应 (SSE)
- `GET /api/conversations` - 获取对话列表
- `GET /api/conversations/{id}` - 获取特定对话
- `GET /api/agents` - 获取可用智能体列表
- `GET /api/agents/{name}` - 获取智能体详情

### 异常处理

使用自定义异常 (`server/api/exceptions.py`):

```python
from .exceptions import APIException

# 抛出异常
raise APIException(
    status_code=400,
    error_code="INVALID_INPUT",
    message="Invalid query format"
)
```

## 日志和调试

### 日志配置

使用 `loguru` 进行结构化日志:

```python
from loguru import logger

logger.info("Processing request", query=user_query)
logger.warning("API rate limit approaching", remaining=10)
logger.error("Failed to process", exc_info=True)
```

### 日志位置

- 智能体日志: `../logs/{timestamp}/{AgentName}.log`
- 服务器日志: 标准输出 (stdout)

### 调试技巧

```bash
# 实时查看日志
tail -f ../logs/*/ResearchAgent.log

# Windows PowerShell
Get-Content ..\logs\*\ResearchAgent.log -Wait -Tail 50

# 搜索错误
grep -r "ERROR" ../logs/
# Windows PowerShell
Select-String -Path "..\logs\*\*.log" -Pattern "ERROR"

# 启用详细日志 (设置环境变量)
export LOG_LEVEL=DEBUG
uv run valuecell/server/main.py
```

### 使用 Python 调试器

```bash
# 使用 ipdb
uv add --dev ipdb
# 在代码中添加断点
import ipdb; ipdb.set_trace()

# 或使用内置 pdb
import pdb; pdb.set_trace()

# 运行时启用调试
uv run python -m pdb valuecell/server/main.py
```

## 代码规范

### Python 编码规范

- **类型注解**: 充分使用类型注解,所有公共函数都应有类型提示
- **Pydantic 模型**: 数据结构全部定义为 Pydantic BaseModel
- **异步优先**: 所有 I/O 操作使用 `async`/`await`
- **文档字符串**: 使用 Google 风格的 docstring
- **文件大小**: 每个文件不超过 300 行
- **函数长度**: 每个函数不超过 50 行
- **禁止裸 dict**: 避免使用未定义结构的 dict,使用 Pydantic 模型

### 文件组织

- 每层文件夹中的文件不超过 8 个
- 如有超过,规划为多层子文件夹
- 相关功能组织在同一目录下

### 导入顺序 (isort)

```python
# 1. 标准库
import os
from typing import Optional

# 2. 第三方库
from fastapi import FastAPI
from pydantic import BaseModel

# 3. 本地导入
from valuecell.core.types import UserInput
from valuecell.utils import generate_id
```

### 避免代码坏味道

- **僵化** (Rigidity): 系统难以变更
- **冗余** (Redundancy): 重复的代码逻辑
- **循环依赖** (Circular Dependency): 模块互相纠缠
- **脆弱性** (Fragility): 一处修改导致其他部分损坏
- **晦涩性** (Obscurity): 代码意图不明
- **数据泥团** (Data Clump): 多个数据项总是一起出现,应组合成对象

## 第三方智能体集成

### 隔离虚拟环境

⚠️ **重要**: 第三方智能体应使用独立的虚拟环境,避免依赖冲突。

```bash
# ai-hedge-fund
cd third_party/ai-hedge-fund
uv venv --python 3.12
uv sync
uv pip list

# TradingAgents
cd third_party/TradingAgents
uv venv --python 3.12
uv sync
uv pip list
```

### 启动第三方智能体

```bash
# AI-Hedge-Fund: Warren Buffett 风格
cd third_party/ai-hedge-fund
uv run --env-file ../../.env -m adapter --analyst warren_buffett

# 其他分析师
uv run --env-file ../../.env -m adapter --analyst charlie_munger
uv run --env-file ../../.env -m adapter --analyst peter_lynch
```

## 常见问题排查

### 依赖问题

```bash
# 同步失败 - 强制重新安装
uv sync --group dev --reinstall

# 清除缓存
uv cache clean

# 验证虚拟环境
which python  # 应指向 .venv/bin/python
uv run python --version  # 应显示 Python 3.12+
```

### 数据库问题

```bash
# 数据库锁定
rm ../valuecell.db-shm ../valuecell.db-wal
uv run valuecell/server/db/init_db.py

# 向量数据库损坏
rm -rf ../.lancedb/
# 重启智能体会自动重建
```

### 端口占用

```bash
# 检查端口占用
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 修改端口 (在 ../.env 中)
API_PORT=8001
```

### 智能体启动失败

1. **检查 API 密钥**: 确认 `.env` 中的 LLM 提供商密钥正确
2. **检查日志**: 查看 `../logs/` 中的错误信息
3. **验证配置**: 运行 `uv run python -c "from valuecell.server.config.settings import get_settings; print(get_settings())"`
4. **检查端口**: 确保智能体端口未被占用

### 导入错误

```bash
# 确保在 python/ 目录下运行
pwd  # 应显示 .../valuecell/python

# 使用 uv run 而不是直接 python
uv run python -m valuecell.agents.research_agent

# 检查 PYTHONPATH
echo $PYTHONPATH  # 应包含当前目录
```

## 性能优化

### 异步并发

```python
import asyncio

# 并发执行多个任务
results = await asyncio.gather(
    fetch_data_1(),
    fetch_data_2(),
    fetch_data_3()
)
```

### 响应流式传输

```python
async def stream_response():
    """流式传输响应,避免内存积累"""
    for chunk in process_large_data():
        yield StreamResponse(
            content=chunk,
            event=StreamResponseEvent.MESSAGE_CHUNK
        )
```

### 数据库连接池

SQLAlchemy 自动管理连接池,配置在 `server/db/models.py`:
```python
engine = create_async_engine(
    database_url,
    pool_size=5,
    max_overflow=10
)
```

## 安全注意事项

- ⚠️ **永远不要提交 `.env` 文件** 到 git
- ⚠️ **API 密钥应通过环境变量传递**
- ⚠️ **生产环境必须使用 HTTPS**
- ⚠️ **输入验证**: 所有用户输入都应通过 Pydantic 验证
- ⚠️ **SQL 注入**: 使用 SQLAlchemy ORM,避免原始 SQL
- ⚠️ **敏感日志**: 不要在日志中记录 API 密钥或用户密码

## 文档

- **核心架构**: `../docs/CORE_ARCHITECTURE.md`
- **配置指南**: `../docs/CONFIGURATION_GUIDE.md`
- **OKX 交易**: `../docs/OKX_SETUP.md`
- **Python 包说明**: `README.md`

## 参考资源

- **FastAPI 文档**: https://fastapi.tiangolo.com/
- **Pydantic 文档**: https://docs.pydantic.dev/
- **SQLAlchemy 文档**: https://docs.sqlalchemy.org/
- **agno 文档**: https://github.com/agno-ai/agno
- **a2a-sdk 文档**: https://github.com/a2a-protocol/a2a-sdk
- **uv 文档**: https://docs.astral.sh/uv/
