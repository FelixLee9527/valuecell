# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

ValueCell 是一个社区驱动的多智能体金融应用平台，核心使命是构建全球最大的去中心化金融智能体社区。

**技术栈**:
- 后端: Python 3.12+ + FastAPI + SQLAlchemy + Pydantic + `agno` v2.0 + `a2a-sdk`
- 前端: React 19 + TypeScript + Tailwind CSS v4 + React Router v7
- 包管理: `uv` (Python), `bun` (JavaScript/TypeScript)
- 数据存储: SQLite (对话历史) + LanceDB (向量知识库)

## 常用命令

### 项目启动

**Linux / macOS**:
```bash
bash start.sh
```

**Windows (PowerShell)**:
```powershell
.\start.ps1
```

启动脚本会自动:
1. 检查并安装 `bun` 和 `uv` (如果缺失)
2. 运行 `python/scripts/prepare_envs.sh` 初始化环境
3. 同步 Python 依赖 (`uv sync --group dev`)
4. 初始化数据库 (`valuecell/server/db/init_db.py`)
5. 安装前端依赖 (`bun install`)
6. 启动后端 (`uv run --with questionary scripts/launch.py`)
7. 启动前端 (`bun run dev`)

**访问地址**:
- Web UI: http://localhost:1420
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 日志: `logs/{timestamp}/`

### Python 后端开发

**目录**: `python/`

```bash
cd python

# 依赖管理
uv sync                    # 同步生产依赖
uv sync --group dev       # 同步开发依赖
uv sync --group test      # 同步测试依赖

# 启动交互式智能体选择器
uv run --with questionary scripts/launch.py

# 初始化数据库
uv run valuecell/server/db/init_db.py

# 代码质量检查
ruff check .              # 检查代码质量
ruff format .             # 格式化代码

# 测试
pytest                    # 运行所有测试
pytest --cov             # 生成覆盖率报告
pytest path/to/test.py   # 运行单个测试文件
pytest -k test_name      # 运行特定测试
```

**重要**: 所有 Python 操作必须使用 `uv`，禁止使用 `pip`、`poetry`、`conda`、`python3`、`python` 命令。

### 前端开发

**目录**: `frontend/`

```bash
cd frontend

# 依赖管理
bun install              # 安装依赖

# 开发
bun run dev              # 启动开发服务器
bun run build            # 生产构建
bun run typecheck        # TypeScript 类型检查
bun run lint:fix         # 代码检查和自动修复
```

**重要**: 所有前端操作必须使用 `bun`，禁止使用 `npm`、`yarn`、`pnpm`。

## 核心架构

### 多智能体协调流程

```
用户输入
  ↓
Orchestrator (编排器) - coordinate/orchestrator.py
  ↓
SuperAgent (快速分类) - core/super_agent/
  ├→ 直接回答 → ResponseBuffer → 持久化 + 流式输出到 UI
  └→ 转交规划 (enriched query)
       ↓
Planner (规划器) - core/plan/
  ├→ 需要用户输入 → HITL (人在回路)
  └→ 生成执行计划
       ↓
TaskExecutor (任务执行) - core/task/
  ├→ A2A Protocol (智能体间通信)
  └→ 调用远程智能体
       ↓
ResponseRouter (响应路由) - core/event/
  ↓
ResponseBuffer (响应缓存) - core/event/
  ↓
ConversationStore (对话记忆) - core/conversation/
  ↓
UI + 用户
```

### 目录结构

```
python/
├── valuecell/
│   ├── agents/              # 智能体实现 (研究、交易、新闻等)
│   ├── core/                # 核心编程模型
│   │   ├── coordinate/      # Orchestrator 编排器
│   │   ├── super_agent/     # SuperAgent 快速分类
│   │   ├── plan/            # Planner 规划器
│   │   ├── task/            # TaskExecutor 任务执行
│   │   ├── event/           # ResponseRouter/ResponseBuffer 事件处理
│   │   ├── conversation/    # ConversationStore 对话记忆
│   │   └── agent/           # Agent 装饰器和工具
│   ├── server/              # FastAPI 后端服务
│   │   ├── main.py          # 服务入口 (uvicorn)
│   │   ├── api/             # REST API (routers, schemas, app)
│   │   ├── config/          # 配置管理 (settings.py)
│   │   ├── db/              # 数据库 (models, init_db.py)
│   │   └── services/        # 业务逻辑服务
│   ├── adapters/            # 外部适配器 (models, assets)
│   ├── configs/             # YAML 配置文件
│   │   ├── config.yaml      # 全局配置
│   │   ├── providers/       # LLM 提供商配置
│   │   ├── agents/          # 智能体配置
│   │   └── locales/         # 国际化 (en-US, zh-Hans, ja)
│   └── utils/               # 工具函数
├── scripts/
│   ├── launch.py            # 交互式智能体启动器
│   └── prepare_envs.sh      # 环境初始化脚本
└── third_party/             # 第三方智能体

frontend/
├── src/
│   ├── routes/              # React Router 路由
│   ├── components/          # React 组件
│   │   └── valuecell/       # ValueCell 特定组件
│   ├── assets/              # 静态资源
│   └── styles/              # 样式文件
└── build/                   # 构建输出
```

### 关键模块职责

| 模块 | 文件路径 | 职责 |
|------|---------|------|
| **Orchestrator** | `core/coordinate/orchestrator.py` | 协调整个流程，管理状态转移 |
| **SuperAgent** | `core/super_agent/` | 快速判断是否需要规划，提供上下文充实 |
| **Planner** | `core/plan/planner.py` | 根据用户意图生成执行计划，支持 HITL |
| **TaskExecutor** | `core/task/executor.py` | 执行计划中的各个任务，支持定时任务 |
| **ResponseRouter** | `core/event/` | 将远程事件转换为统一的响应 |
| **ConversationStore** | `core/conversation/` | 持久化对话历史 (SQLite + LanceDB) |
| **EventResponseService** | `core/event/` | 事件映射、缓存和路由 |

### 异步和可重入设计

- 所有外部调用都是 `async`/`await`，支持并发
- 后台生产者独立于客户端连接运行
- 支持 HITL（人在回路），可暂停并恢复
- ResponseBuffer 支持稳定 ID 和部分聚合
- 智能体位置透明（本地/远程可互换）

### Agent-to-Agent (A2A) 协议

- 使用 `a2a-sdk` 定义任务和消息模式
- 支持 HTTP 和其他传输方式
- 智能体位置透明（本地/远程可互换）
- 流式响应管道: A2A Task Events → ResponseRouter → ResponseBuffer → Store → UI

## 配置管理

### 三层配置系统 (优先级从高到低)

1. **环境变量** - 运行时覆盖
2. **.env 文件** - 用户级配置
3. **YAML 文件** - 系统默认值 (`python/valuecell/configs/`)

### 环境变量配置

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 添加必要的 API 密钥
```

**必需配置**:
- **LLM 提供商** (多选一): `OPENROUTER_API_KEY` (推荐) / `SILICONFLOW_API_KEY` / `GOOGLE_API_KEY` / `OPENAI_API_KEY` / `AZURE_OPENAI_API_KEY`
- **研究智能体**: `SEC_EMAIL` (用于 SEC API 请求)
- **交易智能体**: `OKX_*` 环境变量 (参考 [docs/OKX_SETUP.md](docs/OKX_SETUP.md))

**其他配置**:
- `LANG`: 语言设置 (en-US, zh-Hans, zh-Hant, ja)
- `TIMEZONE`: 时区设置
- `API_HOST`, `API_PORT`: 后端服务地址和端口

详细配置说明: [docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md)

## 代码规范

### Python

- **包管理**: 仅使用 `uv`，禁止 `pip`/`poetry`/`conda`
- **虚拟环境**: 统一使用 `.venv` 作为目录名
- **类型安全**: 充分使用 Pydantic 进行数据验证和类型提示
- **数据结构**: 尽可能全部定义成强类型。如果不得不使用未经结构化定义的 dict，需要先征求用户同意
- **代码风格**: 使用 `ruff` 进行检查和格式化
  - 行长限制: 88 字符
  - 目标版本: Python 3.12
  - 缩进: 4 空格
- **异步优先**: 所有 I/O 操作都使用 `async`/`await`
- **排除目录**: venv, build, dist, node_modules, site-packages, third_party

### TypeScript/JavaScript

- **包管理**: 仅使用 `bun`，禁止 `npm`/`yarn`/`pnpm`
- **模块系统**: 严禁使用 CommonJS，仅使用 ES modules
- **类型安全**: TypeScript 严格模式，数据结构全部定义成强类型
- **数据结构**: 尽可能全部定义成强类型。如果不得不使用 `any` 或未经结构化定义的 json，需要先征求用户同意
- **代码风格**: 使用 `Biome` 进行检查和格式化
- **路径别名**: `@/*` 和 `@valuecell/*`
- **React 版本**: React 19 (严格要求)
- **Tailwind CSS**: v4 (严格要求)

## 架构原则

### 文件大小限制

- **Python**: 每个文件不超过 300 行
- **TypeScript/JavaScript**: 每个文件不超过 300 行
- **静态语言** (Java, Go, Rust): 每个文件不超过 400 行

### 目录组织

- 每层文件夹中的文件，尽可能不超过 8 个
- 如有超过，需要规划为多层子文件夹

### 避免代码坏味道

- **僵化** (Rigidity): 系统难以变更，任何微小改动都会引发连锁修改
- **冗余** (Redundancy): 同样代码逻辑在多处重复出现
- **循环依赖** (Circular Dependency): 模块互相纠缠，难以解耦
- **脆弱性** (Fragility): 一处修改导致其他无关部分功能损坏
- **晦涩性** (Obscurity): 代码意图不明，结构混乱
- **数据泥团** (Data Clump): 多个数据项总是一起出现，应组合成独立对象
- **不必要的复杂性** (Needless Complexity): 过度设计使系统臃肿

**重要**: 一旦识别出这些「坏味道」，应立即询问用户是否需要优化，并给出合理的优化建议。

### 分层架构

1. **API 层**: routers, schemas
2. **服务层**: services, orchestrators
3. **核心逻辑层**: agents, planners, executors
4. **数据层**: models, stores

## 智能体开发

### 添加新智能体

1. **创建智能体实现**: `python/valuecell/agents/{agent_name}.py`
2. **定义 Agent Card**: `python/valuecell/configs/agent_cards/{agent_name}.yaml`
3. **添加智能体配置**: `python/valuecell/configs/agents/{agent_name}.yaml`
4. **使用装饰器**: `@agent` 装饰器 (来自 `core/agent/decorator.py`)
5. **注册连接**: 使用 `core/agent/connect.py` 进行注册和路由
6. **A2A 集成**: 定义任务和消息模式，使用 `a2a-sdk`

### 智能体类型

- **SuperAgent**: 快速分类和上下文充实
- **ResearchAgent**: 基于财务文档的研究分析
- **AutoTradingAgent**: 基于技术指标的自动交易
- **NewsAgent**: 定时新闻推送
- **AI-HedgeFund Agents**: 基于著名投资者风格的分析
- **TradingAgents**: 市场分析、情感分析等

## 日志和调试

- 所有日志输出到 `logs/{timestamp}/` 目录
- 每个智能体一个日志文件
- 使用 `loguru` 进行结构化日志
- 日志在启动脚本中自动配置

## 数据存储

- **对话历史**: SQLite (`valuecell.db`)
- **向量知识库**: LanceDB (`.lancedb/` 目录)
- **日志**: 按时间戳保存到 `logs/` 目录

**注意**: 如果长时间未更新，可以删除这些数据库文件重新启动:
- `lancedb/`
- `valuecell.db`
- `.knowledgebase/`

## 国际化

支持语言 (通过 YAML 配置):
- English (en-US)
- 中文简体 (zh-Hans)
- 中文繁体 (zh-Hant)
- 日本語 (ja)

配置文件: `python/valuecell/configs/locales/`

## 实时交易 (OKX Preview)

- 设置 `AUTO_TRADING_EXCHANGE=okx`
- 填写 `.env` 中的 `OKX_*` 凭证
- 保持 `OKX_ALLOW_LIVE_TRADING=false` 直到纸上交易验证通过
- 参考: [docs/OKX_SETUP.md](docs/OKX_SETUP.md)

## 文档

- **核心架构**: [docs/CORE_ARCHITECTURE.md](docs/CORE_ARCHITECTURE.md)
- **配置指南**: [docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md)
- **OKX 设置**: [docs/OKX_SETUP.md](docs/OKX_SETUP.md)
- **正式文档**: 写到 `docs/` 目录
- **讨论方案**: 写到 `discuss/` 目录

## 社区

- **Discord**: https://discord.com/invite/84Kex3GGAh
- **Twitter**: @valuecell
- **GitHub Issues**: https://github.com/ValueCell-ai/valuecell/issues

## 重要提醒

- ⚠️ ValueCell 团队成员不会主动联系社区参与者
- ⚠️ 本项目仅用于技术交流
- ⚠️ 投资有风险，决策需谨慎
