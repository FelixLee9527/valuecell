# CLAUDE.md - Frontend

本文件为 Claude Code (claude.ai/code) 提供前端代码库工作指南。

## 项目概述

ValueCell 前端是一个基于 React 19 和 React Router v7 构建的单页应用 (SPA)，为用户提供与多智能体金融平台的交互界面。

**技术栈**:
- **框架**: React 19 + React Router v7 (SPA 模式)
- **语言**: TypeScript (严格模式)
- **样式**: Tailwind CSS v4 + @tailwindcss/typography
- **UI 组件**: Radix UI + shadcn/ui
- **状态管理**: Zustand
- **数据获取**: @tanstack/react-query (TanStack Query)
- **图表**: ECharts
- **实时通信**: Server-Sent Events (SSE)
- **桌面应用**: Tauri v2 (可选)
- **包管理**: Bun 1.3.0
- **代码质量**: Biome (格式化 + 检查)

## 快速开始

### 安装依赖

```bash
bun install
```

### 开发模式

```bash
bun run dev
```

访问: http://localhost:1420

### 生产构建

```bash
bun run build
```

### 预览生产构建

```bash
bun run start
```

## 开发工具

### 代码质量检查

```bash
# 代码检查
bun run lint              # 仅检查错误
bun run lint:fix          # 自动修复问题

# 代码格式化
bun run format            # 检查格式
bun run format:fix        # 自动格式化

# 全面检查 (检查 + 格式化)
bun run check             # 仅检查
bun run check:fix         # 自动修复

# TypeScript 类型检查
bun run typecheck
```

### Tauri 桌面应用

```bash
bun run tauri dev         # 开发模式
bun run tauri build       # 构建桌面应用
```

## 项目结构

```
frontend/
├── src/
│   ├── root.tsx                    # 根组件 (Layout + QueryClient + SidebarProvider)
│   ├── routes.ts                   # React Router 路由配置
│   ├── global.css                  # 全局样式 (Tailwind 入口)
│   │
│   ├── app/                        # 页面路由
│   │   ├── redirect-to-home.tsx    # 根路径重定向
│   │   ├── home/                   # 首页模块
│   │   │   ├── _layout.tsx         # 首页布局
│   │   │   ├── home.tsx            # 首页 (智能体建议 + 股票列表)
│   │   │   ├── stock.tsx           # 股票详情页
│   │   │   ├── components/         # 首页组件
│   │   │   └── hooks/              # 首页 Hooks
│   │   ├── market/                 # 智能体市场
│   │   │   ├── agents.tsx          # 智能体列表页
│   │   │   └── components/         # 市场组件
│   │   ├── agent/                  # 智能体聊天
│   │   │   ├── chat.tsx            # 聊天页面
│   │   │   ├── config.tsx          # 智能体配置页
│   │   │   └── components/         # 聊天组件
│   │   ├── setting/                # 设置模块
│   │   │   ├── _layout.tsx         # 设置布局
│   │   │   ├── general.tsx         # 通用设置
│   │   │   ├── memory.tsx          # 记忆管理
│   │   │   └── components/         # 设置组件
│   │   └── test.tsx                # 测试组件页
│   │
│   ├── components/                 # 组件库
│   │   ├── ui/                     # 基础 UI 组件 (shadcn/ui)
│   │   │   ├── avatar.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── sidebar.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── ...
│   │   └── valuecell/              # ValueCell 特定组件
│   │       ├── app-sidebar.tsx     # 应用侧边栏
│   │       ├── agent-avatar.tsx    # 智能体头像
│   │       ├── svg-icon.tsx        # SVG 图标组件
│   │       ├── button/             # 自定义按钮
│   │       ├── menus/              # 菜单组件
│   │       ├── charts/             # 图表组件 (ECharts)
│   │       ├── renderer/           # 消息渲染器
│   │       ├── scroll/             # 滚动容器
│   │       └── skeleton/           # 骨架屏
│   │
│   ├── api/                        # API 客户端
│   │   ├── agent.ts                # 智能体 API
│   │   ├── conversation.ts         # 对话 API
│   │   ├── setting.ts              # 设置 API
│   │   └── stock.ts                # 股票 API
│   │
│   ├── lib/                        # 工具库
│   │   ├── api-client.ts           # HTTP 客户端封装
│   │   ├── sse-client.ts           # SSE 客户端封装
│   │   ├── agent-store.ts          # 智能体状态存储
│   │   ├── utils.ts                # 通用工具函数 (cn, etc.)
│   │   └── time.ts                 # 时间处理工具
│   │
│   ├── hooks/                      # 自定义 Hooks
│   │   ├── use-sse.ts              # SSE 连接 Hook
│   │   ├── use-mobile.ts           # 移动端检测
│   │   ├── use-chart-resize.ts     # 图表响应式
│   │   └── use-debounce.ts         # 防抖 Hook
│   │
│   ├── assets/                     # 静态资源
│   │   ├── png/                    # PNG 图片
│   │   │   ├── agents/             # 智能体头像
│   │   │   └── ...
│   │   └── svg/                    # SVG 图标
│   │
│   └── types/                      # TypeScript 类型定义
│
├── public/                         # 公共静态资源
│   └── logo.svg                    # Logo
│
├── src-tauri/                      # Tauri 桌面应用
│   ├── src/                        # Rust 源码
│   ├── icons/                      # 应用图标
│   ├── tauri.conf.json             # Tauri 配置
│   └── Cargo.toml                  # Rust 依赖
│
├── react-router.config.ts          # React Router 配置
├── biome.json                      # Biome 配置
├── components.json                 # shadcn/ui 配置
├── package.json                    # 依赖和脚本
└── tsconfig.json                   # TypeScript 配置
```

## 核心架构

### 路由系统

使用 **React Router v7** 的文件系统路由 (在 [src/routes.ts](src/routes.ts) 中配置):

| 路由 | 文件 | 描述 |
|------|------|------|
| `/` | `app/redirect-to-home.tsx` | 重定向到 `/home` |
| `/home` | `app/home/home.tsx` | 首页 (智能体建议 + 股票列表) |
| `/home/stock/:stockId` | `app/home/stock.tsx` | 股票详情页 |
| `/market` | `app/market/agents.tsx` | 智能体市场 |
| `/agent/:agentName` | `app/agent/chat.tsx` | 智能体聊天 |
| `/agent/:agentName/config` | `app/agent/config.tsx` | 智能体配置 |
| `/setting` | `app/setting/general.tsx` | 通用设置 |
| `/setting/memory` | `app/setting/memory.tsx` | 记忆管理 |
| `/test` | `app/test.tsx` | 测试组件 |

**注意**: 应用运行在 **SPA 模式** (SSR 关闭)，见 [react-router.config.ts](react-router.config.ts:6)。

### 状态管理

#### 1. **Zustand** - 客户端状态

用于智能体状态管理，见 [src/lib/agent-store.ts](src/lib/agent-store.ts)。

#### 2. **TanStack Query** - 服务端状态

全局配置在 [src/root.tsx](src/root.tsx:30-42):
- `staleTime`: 5 分钟 (数据保持新鲜时间)
- `gcTime`: 30 分钟 (垃圾回收时间)
- `refetchOnWindowFocus`: false (窗口聚焦不自动刷新)
- `retry`: 查询重试 2 次，变更重试 1 次

### 实时通信 (SSE)

#### SSE 客户端封装

见 [src/lib/sse-client.ts](src/lib/sse-client.ts) 和 [src/hooks/use-sse.ts](src/hooks/use-sse.ts)。

**核心流程**:
1. 用户发送消息 → POST `/api/conversations/{id}/messages`
2. 前端建立 SSE 连接 → GET `/api/sse/messages/{messageId}/stream`
3. 后端推送事件流 → 前端逐步渲染

**事件类型** (对应后端 `EventType`):
- `agent_response`: 智能体文本响应
- `tool_call`: 工具调用
- `scheduled_task`: 定时任务
- `plan`: 执行计划
- `hitl`: 人在回路 (需要用户输入)
- `stream_end`: 流结束
- `stream_error`: 流错误

### 消息渲染系统

见 [src/components/valuecell/renderer/](src/components/valuecell/renderer/)。

**渲染器映射** (在 [index.tsx](src/components/valuecell/renderer/index.tsx) 中):

| 事件类型 | 渲染器 | 描述 |
|----------|--------|------|
| `agent_response` | `MarkdownRenderer` | Markdown 文本 (支持 GFM) |
| `tool_call` | `ToolCallRenderer` | 工具调用详情 |
| `scheduled_task` | `ScheduledTaskRenderer` | 定时任务卡片 |
| `plan` | `ScheduledTaskControllerRenderer` | 执行计划控制器 |
| `model_trade` | `ModelTradeRenderer` / `ModelTradeTableRenderer` | 交易信号 |
| `report` | `ReportRenderer` | 研究报告 |
| `conversation` | `ChatConversationRenderer` | 对话消息 |
| 其他 | `UnknownRenderer` | 未知类型降级 |

**扩展指南**:
1. 创建新渲染器组件 (如 `NewTypeRenderer.tsx`)
2. 在 [index.tsx](src/components/valuecell/renderer/index.tsx) 中注册
3. 确保后端 `EventType` 和前端类型定义一致

### API 客户端

#### HTTP 客户端

见 [src/lib/api-client.ts](src/lib/api-client.ts)。

**基础 URL**: `http://localhost:8000` (环境变量可配置)

**核心方法**:
- `apiClient.get<T>(url)`
- `apiClient.post<T>(url, data)`
- `apiClient.put<T>(url, data)`
- `apiClient.delete<T>(url)`

#### API 模块

| 模块 | 文件 | 主要功能 |
|------|------|----------|
| 智能体 | [src/api/agent.ts](src/api/agent.ts) | 获取智能体列表、详情、配置 |
| 对话 | [src/api/conversation.ts](src/api/conversation.ts) | 创建对话、发送消息、获取历史 |
| 设置 | [src/api/setting.ts](src/api/setting.ts) | 获取/更新设置、清理记忆 |
| 股票 | [src/api/stock.ts](src/api/stock.ts) | 搜索股票、获取详情、价格历史 |

### UI 组件库

#### 基础组件 (shadcn/ui)

位于 [src/components/ui/](src/components/ui/)，基于 Radix UI 构建。

**注意**: Biome 配置中排除了 `ui/` 目录的检查 (见 [biome.json:6](biome.json:6))，因为这些是第三方组件。

#### ValueCell 自定义组件

位于 [src/components/valuecell/](src/components/valuecell/)。

**核心组件**:
- **app-sidebar.tsx**: 应用侧边栏 (导航菜单 + 对话历史)
- **agent-avatar.tsx**: 智能体头像 (自动映射图片)
- **svg-icon.tsx**: SVG 图标组件 (支持动态加载)
- **charts/**: ECharts 封装
  - `sparkline.tsx`: 迷你走势图
  - `mini-sparkline.tsx`: 更小的走势图
  - `model-multi-line.tsx`: 多线图
- **renderer/**: 消息渲染器 (详见上文)
- **scroll/**: 滚动容器 (基于 OverlayScrollbars)

### 图表系统

使用 **ECharts 6.x**，封装在 [src/components/valuecell/charts/](src/components/valuecell/charts/)。

**响应式处理**: 使用 `use-chart-resize` Hook (见 [src/hooks/use-chart-resize.ts](src/hooks/use-chart-resize.ts))。

**示例**: 股票走势图

```tsx
import { Sparkline } from "@/components/valuecell/charts/sparkline";

<Sparkline
  data={priceHistory}
  width={300}
  height={100}
  color="#10b981"
/>
```

## 代码规范

### TypeScript

- **严格模式**: 启用 `strict` 和所有严格检查
- **类型优先**: 所有数据结构必须定义强类型
- **禁止 `any`**: 除非征得用户同意，否则禁止使用 `any`
- **路径别名**:
  - `@/*` → `src/*`
  - `@valuecell/*` → `src/components/valuecell/*`

### React

- **版本**: React 19 (严格要求)
- **函数组件**: 优先使用函数组件 + Hooks
- **Props 类型**: 所有组件必须定义 Props 类型
- **异步操作**: 使用 TanStack Query 或 `useEffect` + cleanup
- **避免内联函数**: 大型组件中使用 `useCallback` 优化

### Tailwind CSS

- **版本**: Tailwind CSS v4 (严格要求)
- **插件**: `@tailwindcss/typography` (Markdown 样式)
- **工具函数**: 使用 `cn()` 合并类名 (见 [src/lib/utils.ts](src/lib/utils.ts))
- **响应式**: 优先使用 Tailwind 响应式类 (`sm:`, `md:`, `lg:`)
- **暗色模式**: 支持 `next-themes` (通过 `dark:` 类)

**示例**:

```tsx
import { cn } from "@/lib/utils";

<div className={cn(
  "rounded-lg p-4",
  "bg-white dark:bg-gray-800",
  "transition-colors",
  isActive && "border-blue-500"
)} />
```

### Biome 配置

见 [biome.json](biome.json)。

**核心规则**:
- **引号**: 双引号 (JS/TS) + 双引号 (JSX)
- **缩进**: 2 空格
- **未使用导入**: 自动删除 (warn 级别)
- **Tailwind 类排序**: 强制排序 (error 级别)
- **禁止 `var`**: 强制使用 `const`/`let` (error 级别)
- **React 依赖**: 检查 `useEffect` 依赖 (warn 级别)

**排除目录**:
- `src/components/magicui` (第三方 UI)
- `src/components/ui` (shadcn/ui)

### 文件大小限制

**硬性指标**: 每个 TypeScript/TSX 文件不超过 **300 行**。

如果文件过大:
1. 拆分组件 (提取子组件)
2. 提取 Hooks (逻辑复用)
3. 提取工具函数 (移到 `lib/` 或 `utils/`)

### 命名约定

- **组件**: PascalCase (如 `AgentAvatar`)
- **文件名**: kebab-case (如 `agent-avatar.tsx`)
- **Hooks**: camelCase + `use` 前缀 (如 `useSSE`)
- **常量**: UPPER_SNAKE_CASE (如 `API_BASE_URL`)
- **类型/接口**: PascalCase (如 `AgentConfig`)

### 避免代码坏味道

参考项目根目录 [CLAUDE.md](../CLAUDE.md) 的「避免代码坏味道」章节。

**前端特定问题**:
- **Props drilling**: 超过 3 层传递考虑 Context 或 Zustand
- **重复渲染**: 使用 `React.memo` 或 `useMemo` 优化
- **未清理副作用**: `useEffect` 必须返回 cleanup 函数
- **内联对象/数组**: 避免在渲染中创建新对象 (使用 `useMemo`)

## 开发工作流

### 添加新页面

1. 在 `src/app/` 创建页面文件 (如 `my-page.tsx`)
2. 在 [src/routes.ts](src/routes.ts) 添加路由配置
3. 在侧边栏 ([src/components/valuecell/app-sidebar.tsx](src/components/valuecell/app-sidebar.tsx)) 添加导航

### 添加新 API

1. 在 `src/api/` 创建 API 模块 (如 `my-api.ts`)
2. 定义 TypeScript 类型 (响应/请求)
3. 使用 `apiClient` 封装请求
4. 在组件中使用 TanStack Query 调用

**示例**:

```tsx
// src/api/my-api.ts
import { apiClient } from "@/lib/api-client";

export interface MyData {
  id: string;
  name: string;
}

export const getMyData = async (): Promise<MyData[]> => {
  return apiClient.get<MyData[]>("/api/my-data");
};

// 组件中使用
import { useQuery } from "@tanstack/react-query";
import { getMyData } from "@/api/my-api";

const { data, isLoading } = useQuery({
  queryKey: ["myData"],
  queryFn: getMyData,
});
```

### 添加新消息渲染器

1. 在 `src/components/valuecell/renderer/` 创建渲染器 (如 `my-type-renderer.tsx`)
2. 在 [index.tsx](src/components/valuecell/renderer/index.tsx) 注册
3. 确保后端 `EventType` 一致

**模板**:

```tsx
// src/components/valuecell/renderer/my-type-renderer.tsx
import type { FC } from "react";

interface MyTypeRendererProps {
  data: any; // 替换为具体类型
}

export const MyTypeRenderer: FC<MyTypeRendererProps> = ({ data }) => {
  return (
    <div className="rounded-lg border p-4">
      {/* 渲染逻辑 */}
    </div>
  );
};
```

### 添加新图表

1. 在 `src/components/valuecell/charts/` 创建图表组件
2. 使用 `use-chart-resize` Hook 处理响应式
3. 使用 ECharts 配置对象

**模板**:

```tsx
import type { FC } from "react";
import { useEffect, useRef } from "react";
import * as echarts from "echarts";
import { useChartResize } from "@/hooks/use-chart-resize";

interface MyChartProps {
  data: number[];
  width?: number;
  height?: number;
}

export const MyChart: FC<MyChartProps> = ({ data, width, height }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstanceRef = useRef<echarts.ECharts | null>(null);

  useChartResize(chartInstanceRef);

  useEffect(() => {
    if (!chartRef.current) return;

    const chart = echarts.init(chartRef.current);
    chartInstanceRef.current = chart;

    chart.setOption({
      // ECharts 配置
      xAxis: { type: "category" },
      yAxis: { type: "value" },
      series: [{ type: "line", data }],
    });

    return () => {
      chart.dispose();
    };
  }, [data]);

  return <div ref={chartRef} style={{ width, height }} />;
};
```

## 调试和测试

### 浏览器调试

1. 打开开发者工具 (F12)
2. 使用 React DevTools 检查组件
3. 使用 TanStack Query DevTools 检查查询状态

### SSE 调试

1. 在浏览器 Network 面板查看 SSE 连接
2. 使用 `console.log` 在 [use-sse.ts](src/hooks/use-sse.ts) 中打印事件
3. 检查后端日志 (`logs/{timestamp}/`)

### 错误处理

- **API 错误**: 使用 TanStack Query 的 `error` 状态
- **SSE 错误**: 监听 `stream_error` 事件
- **全局错误**: 使用 React Error Boundary (TODO: 未实现)

## 性能优化

### 代码分割

React Router v7 自动按路由分割代码。

### 图片优化

- 使用 WebP 格式 (如果支持)
- 智能体头像懒加载

### 列表优化

- 使用虚拟滚动 (长列表)
- 使用 `React.memo` 优化列表项

### 查询优化

- 合理设置 `staleTime` 和 `gcTime`
- 使用 `keepPreviousData` 保持上一次数据
- 使用 `enabled` 控制查询时机

## 构建和部署

### Web 应用

```bash
# 构建
bun run build

# 输出目录
build/client/              # 静态文件 (部署到 CDN)
build/server/              # 服务端文件 (React Router 服务器)

# 预览
bun run start
```

### Tauri 桌面应用

```bash
# 开发
bun run tauri dev

# 构建
bun run tauri build

# 输出目录
src-tauri/target/release/  # 可执行文件
```

## 环境变量

前端环境变量通过 Vite 注入。

**配置文件**: `.env` (项目根目录)

**常用变量**:
- `VITE_API_BASE_URL`: 后端 API 地址 (默认: `http://localhost:8000`)

## 国际化 (TODO)

当前版本未实现前端国际化。后端支持多语言 (见 [python/valuecell/configs/locales/](../python/valuecell/configs/locales/))。

**计划**:
- 使用 `react-i18next`
- 从后端 API 获取翻译

## 常见问题

### 1. SSE 连接失败

**原因**: 后端未启动或端口不匹配

**解决**:
1. 确保后端运行在 `http://localhost:8000`
2. 检查 [src/lib/api-client.ts](src/lib/api-client.ts) 中的 `API_BASE_URL`

### 2. 智能体头像不显示

**原因**: 图片文件缺失或路径错误

**解决**:
1. 检查 [src/assets/png/agents/](src/assets/png/agents/) 是否有对应图片
2. 检查 [agent-avatar.tsx](src/components/valuecell/agent-avatar.tsx) 中的映射逻辑

### 3. 类型错误

**原因**: 前后端类型不一致

**解决**:
1. 检查后端 API 响应格式
2. 更新前端类型定义 (在 `src/api/` 或 `src/types/`)

### 4. Tailwind 类不生效

**原因**: Tailwind CSS v4 配置问题

**解决**:
1. 确保 `global.css` 中导入了 Tailwind
2. 重启开发服务器

### 5. Biome 检查失败

**原因**: 代码风格不符合规范

**解决**:
```bash
bun run check:fix  # 自动修复
```

## 贡献指南

### 代码审查清单

- [ ] 所有数据结构定义了强类型
- [ ] 组件文件不超过 300 行
- [ ] 使用 `cn()` 合并 Tailwind 类
- [ ] `useEffect` 返回了 cleanup 函数
- [ ] API 调用使用 TanStack Query
- [ ] 通过 `bun run typecheck` 和 `bun run check`
- [ ] 无明显性能问题 (如重复渲染)

### 提交前检查

```bash
# 1. 类型检查
bun run typecheck

# 2. 代码质量检查 + 自动修复
bun run check:fix

# 3. 构建测试
bun run build

# 4. 手动测试核心功能
```

## 相关文档

- **项目根文档**: [../CLAUDE.md](../CLAUDE.md)
- **核心架构**: [../docs/CORE_ARCHITECTURE.md](../docs/CORE_ARCHITECTURE.md)
- **配置指南**: [../docs/CONFIGURATION_GUIDE.md](../docs/CONFIGURATION_GUIDE.md)
- **React Router v7**: https://reactrouter.com/
- **TanStack Query**: https://tanstack.com/query/latest
- **Tailwind CSS v4**: https://tailwindcss.com/
- **Biome**: https://biomejs.dev/
- **Tauri**: https://v2.tauri.app/

## 重要提醒

- ⚠️ **严格遵守**: React 19 + Tailwind CSS v4 + React Router v7
- ⚠️ **禁止使用**: `npm`/`yarn`/`pnpm`，仅使用 `bun`
- ⚠️ **禁止使用**: CommonJS 模块系统，仅使用 ES modules
- ⚠️ **文件大小**: 每个文件不超过 300 行
- ⚠️ **类型安全**: 禁止使用 `any`，除非征得用户同意
- ⚠️ **代码质量**: 识别到「坏味道」立即询问用户是否优化
