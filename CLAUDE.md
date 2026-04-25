# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Odd** — a Python Agent built from scratch, incrementally. The goal is to learn Agent architecture by implementing each layer manually: model calling → tools → ReAct loop → MCP/Skills → sub-agents → planning → context management.

Current phase: **Phase 3 (Agent Core) complete.**

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Verify each stage independently
python scripts/verify_stage_1.py   # Model layer
python scripts/verify_stage_2.py   # Tool system
python scripts/verify_stage_3.py   # Agent core (ReAct loop)

# Ad-hoc experimentation
python scripts/play.py
```

## Architecture

```
odd/
├── types.py              # Message, ChatResponse, ToolCall, MessageRole
├── config.py             # All config from env vars (API keys, base URLs, model names)
├── models/
│   ├── base.py           # ModelProvider ABC with chat(messages, tools) -> ChatResponse
│   ├── openai.py         # OpenAI-compatible provider (used via MiniMax proxy)
│   └── anthropic.py      # Anthropic provider (different message/tool format from OpenAI)
├── tools/
│   ├── base.py           # Tool ABC + ToolSpec (name, description, JSON Schema params)
│   ├── registry.py       # Global ToolRegistry singleton + register() helper
│   └── builtin/
│       ├── shell.py      # subprocess.run with timeout
│       ├── filesystem.py # read/write/list within workspace
│       ├── fetch_url.py  # HTTP GET with urllib
│       └── python.py     # eval/exec Python snippets, capturing stdout/stderr
├── agent.py              # ReAct loop: think → act → observe, max_rounds limit
├── mcp/                  # Phase 4 (planned, not yet implemented)
├── skills/               # Phase 4 (planned, not yet implemented)
├── planning/             # Phase 6 (planned, not yet implemented)
└── context/              # Phase 7 (planned, not yet implemented)
scripts/
└── verify_stage_*.py     # Independent verification per phase
```

## Key Design Decisions

- **API proxy**: The project uses MiniMax (`api.minimaxi.com`) as a proxy, not direct OpenAI/Anthropic endpoints. Both providers share the same API key. Config is in `.env`.
- **OpenAI-format tools internally**: The Agent always passes tools in OpenAI function-calling format. `AnthropicProvider` converts to Anthropic's `input_schema` format internally.
- **Tool registration is side-effectful**: Builtin tools self-register on import via `register(ToolInstance())` at module level. Importing `odd.tools.builtin.*` populates the global registry automatically.
- **Conda environment**: VS Code is configured to use `conda` for Python environment management (see `.vscode/settings.json`).
- **Single file ≤ 200 lines**: Per the development principles in PLAN.md, split modules when they grow beyond this.

## Development Principles (from PRD/PLAN)

- **Incremental phases**: Each phase must run independently with its own verification script before moving to the next.
- **Minimal implementation**: Only build what the current phase needs. No speculative features.
- **Interface-first**: Define ABCs before concrete implementations so backends are swappable.
