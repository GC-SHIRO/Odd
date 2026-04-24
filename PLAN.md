# Odd 项目详细开发计划

根据 PRD，Odd 是一个**从头逐步构建的 Python Agent**，核心能力围绕：模型调用 → 工具使用 → MCP/Skill → 子 Agent → 计划执行 → 上下文管理。

以下是按阶段拆解的详细计划，遵循**最小原则**，每个阶段可独立运行和验证。

---

## 阶段 1：模型调用层（Model Layer）
**目标**：建立与 LLM 通信的最小抽象，支持灵活切换模型。

- `odd/models/base.py`：定义 `ModelProvider` 抽象基类（`chat(messages) -> response`）
- `odd/models/openai.py` / `odd/models/anthropic.py`：具体实现（从环境变量读取 API Key）
- `odd/types.py`：定义核心数据类型（`Message`, `MessageRole`, `ChatResponse`, `ToolCall` 等）
- `odd/config.py`：最小配置管理（环境变量 + 可选 `.env`）
- **验证标准**：能独立运行一个脚本，发送多轮对话并收到回复

---

## 阶段 2：工具系统（Tool System）
**目标**：让 Agent 能够执行本地命令行操作。

- `odd/tools/base.py`：定义 `Tool` 抽象基类（`name`, `description`, `parameters`, `execute()`）
- `odd/tools/registry.py`：工具注册中心（装饰器式注册，`@tool`）
- `odd/tools/builtin/shell.py`：本地 Shell 命令执行工具（带安全限制，如工作目录锁定）
- `odd/tools/builtin/filesystem.py`：文件读写工具（限定 workspace 内）
- **验证标准**：Agent 循环中，模型能决定调用 Shell 或文件工具，并正确执行

---

## 阶段 3：Agent 核心循环（Agent Core）
**目标**：实现"思考 → 行动 → 观察"的 ReAct 循环。

- `odd/agent.py`：`Agent` 类
  - 持有 `model` 和 `tools`
  - `run(task)` 方法：主循环
  - 构建 system prompt，告知模型可用工具及其 schema
  - 解析模型回复中的工具调用（XML 或 JSON 格式）
  - 执行工具，将结果追加回上下文
  - 支持终止条件（如模型输出 `<done>` 或特定 JSON）
- **验证标准**：给一个任务，Agent 能自主调用 Shell 完成（如"列出当前目录文件"）

---

## 阶段 4：MCP 与 Skill 集成
**目标**：接入外部 MCP Server，复用 Anthropic 的 Skill 规范。

- `odd/mcp/client.py`：MCP 客户端封装（stdio/sse 连接，发现工具）
- `odd/mcp/adapter.py`：将 MCP Tool 转换为内部 `Tool` 接口
- `odd/skills/`：Skill 定义目录（按 Anthropic 规范，每个 skill 含 `SKILL.md` + 可选工具）
- `odd/skills/loader.py`：Skill 加载器（解析 `SKILL.md`，提取工具定义）
- **验证标准**：Agent 能调用通过 MCP 暴露的外部工具（如文件系统 MCP Server）

---

## 阶段 5：子 Agent 机制（Sub-Agent）
**目标**：Agent 能"召唤"子 Agent 协助处理子任务。

- `odd/agent.py` 扩展：
  - `spawn(sub_task, context) -> SubAgent`：创建子 Agent 实例
  - 子 Agent 继承父 Agent 的配置，但拥有独立的上下文
  - 子 Agent 完成后，结果汇总回父 Agent
- `odd/orchestrator.py`（可选，如需要）：简单的任务分发逻辑
- **验证标准**：主 Agent 能将一个子任务委派给子 Agent，子 Agent 独立完成并返回结果

---

## 阶段 6：计划与执行（Planning）
**目标**：Agent 能给自己制定计划并按步骤执行。

- `odd/planning/planner.py`：
  - 接收任务，生成 `Plan`（步骤列表，每步含描述和依赖）
  - `Plan` 数据结构：`steps: List[Step]`，支持串行/并行标记
- `odd/planning/executor.py`：
  - 按依赖顺序执行步骤
  - 每步作为一个子任务，可调用主 Agent 或子 Agent
  - 步骤失败时的重试/回退策略（最小实现：重试 1 次）
- **验证标准**：给一个复杂任务，Agent 先生成计划，再逐步执行并输出结果

---

## 阶段 7：上下文压缩与管理（Context Management）
**目标**：防止上下文过长，智能压缩历史。

- `odd/context/manager.py`：`ContextManager`
  - 维护消息历史
  - 当 token 数接近阈值时触发压缩
- `odd/context/compressor.py`：
  - 策略 1：滑动窗口（丢弃最早的消息，保留 system prompt + 最近 N 轮）
  - 策略 2：摘要（将早期对话压缩为 summary，替换原消息）
- **验证标准**：运行一个长对话（>20 轮），上下文长度被控制在阈值内，且不丢失关键信息

---

## 阶段 8：整合与入口（Integration）
**目标**：提供统一的 CLI 入口。

- `odd/cli.py`：主入口（`python -m odd "任务描述"`）
- `odd/__main__.py`：模块运行支持
- `pyproject.toml` / `requirements.txt`：依赖管理
- **验证标准**：通过命令行直接启动 Odd，完成端到端任务

---

## 目录结构预览

```
odd/
├── __init__.py
├── __main__.py
├── cli.py
├── config.py
├── types.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── openai.py
│   └── anthropic.py
├── tools/
│   ├── __init__.py
│   ├── base.py
│   ├── registry.py
│   └── builtin/
│       ├── shell.py
│       └── filesystem.py
├── mcp/
│   ├── __init__.py
│   ├── client.py
│   └── adapter.py
├── skills/
│   ├── __init__.py
│   └── loader.py
├── agent.py
├── planning/
│   ├── __init__.py
│   ├── planner.py
│   └── executor.py
└── context/
    ├── __init__.py
    ├── manager.py
    └── compressor.py
```

---

## 开发原则（贯穿全程）

1. **逐步构建**：每个阶段必须能独立运行，不依赖后续阶段
2. **最小实现**：每个阶段只实现 PRD 要求的最小功能，不预设扩展
3. **接口优先**：先定义抽象接口，再写具体实现，方便后续替换
4. **单文件不超 200 行**：逻辑复杂时立即拆分模块
5. **每阶段有验证脚本**：`scripts/verify_stage_X.py` 证明当前阶段可用
