# Odd —— 从零构建的 Python AI Agent

**Odd** 是一个从底层逐步构建的 Python AI Agent，目标是通过亲手实现每一层来深入理解 Agent 架构：模型调用层 → 工具系统 → ReAct 循环 → MCP/Skills → 子 Agent → 计划执行 → 上下文管理。

当前进度：**阶段 3（Agent 核心循环）已完成。**

## 为什么叫 Odd？

Odd 意为"奇特的、零散的"——它不是一个生产级框架，而是一个学习项目。每个模块都从零手写，不依赖 LangChain、AutoGPT 等高层框架，只使用最基础的模型 SDK。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制 .env.example 并填写你的 API Key）
cp .env.example .env

# 运行各阶段验证脚本
python scripts/verify_stage_1.py   # 模型调用层
python scripts/verify_stage_2.py   # 工具系统
python scripts/verify_stage_3.py   # Agent 核心循环（ReAct）

# 自由实验
python scripts/play.py
```

## 架构概览

```
odd/
├── types.py              # 核心类型：Message, ChatResponse, ToolCall, MessageRole
├── config.py             # 统一配置管理（从环境变量读取 API Key 等）
├── models/               # 模型调用层
│   ├── base.py           #   ModelProvider 抽象基类
│   ├── openai.py         #   OpenAI 兼容接口实现
│   └── anthropic.py      #   Anthropic 接口实现
├── tools/                # 工具系统
│   ├── base.py           #   Tool 抽象基类 + ToolSpec
│   ├── registry.py       #   全局工具注册中心
│   └── builtin/          #   内置工具
│       ├── shell.py      #     Shell 命令执行
│       ├── filesystem.py #     文件读写
│       ├── fetch_url.py  #     HTTP 请求
│       └── python.py     #     Python 代码执行
├── agent.py              # Agent 核心：ReAct 循环（思考 → 行动 → 观察）
├── mcp/                  # 阶段 4（计划中）
├── skills/               # 阶段 4（计划中）
├── planning/             # 阶段 6（计划中）
└── context/              # 阶段 7（计划中）
```

## 开发路线图

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 模型调用层 —— 封装 OpenAI / Anthropic 接口 | ✅ 完成 |
| 2 | 工具系统 —— 抽象工具定义 + 内置 Shell/文件工具 | ✅ 完成 |
| 3 | Agent 核心循环 —— ReAct 思考-行动-观察循环 | ✅ 完成 |
| 4 | MCP 与 Skill 集成 —— 接入外部 MCP Server | 🔜 计划中 |
| 5 | 子 Agent 机制 —— 委派子任务给子 Agent | 📋 计划中 |
| 6 | 计划与执行 —— 自主制定计划并逐步执行 | 📋 计划中 |
| 7 | 上下文管理 —— 智能压缩长对话历史 | 📋 计划中 |
| 8 | CLI 整合 —— 统一的命令行入口 | 📋 计划中 |

## 关键设计决策

- **API 代理**：通过 MiniMax (`api.minimaxi.com`) 中转 API 调用，而非直连 OpenAI/Anthropic。
- **OpenAI 工具格式**：Agent 内部统一使用 OpenAI function-calling 格式传递工具定义，Anthropic 接口内部做格式转换。
- **工具自注册**：内置工具通过模块级 `register()` 调用自动注册到全局工具注册中心。
- **接口优先**：所有核心组件先定义抽象基类（ABC），保证后端可替换。
- **单文件 ≤ 200 行**：模块超过此限制立即拆分。

## 开发原则

1. **逐步构建**：每个阶段可独立运行和验证
2. **最小实现**：只实现当前阶段需要的功能，不做预测性开发
3. **接口优先**：先定义 ABC，再写具体实现
4. **可验证**：每个阶段配独立的验证脚本

## Contributors

- [GC-SHIRO](https://github.com/GC-SHIRO) — 项目创建者与开发者
- [Claude](https://claude.ai/code) (Anthropic) — AI 辅助开发

## License

MIT
