"""Odd Agent 命令行交互入口。

启动后与 Agent 进行多轮对话，支持工具调用。
"""

import argparse
import sys
import dotenv
# Load .env if present (for local dev).
dotenv.load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Odd Agent CLI")
    parser.add_argument(
        "--provider",
        default="anthropic",
        choices=["openai", "anthropic"],
        help="模型提供者 (默认: anthropic)",
    )
    args = parser.parse_args()

    # 延迟导入，避免无意义的环境变量检查
    from odd.config import config
    from odd.agent import Agent
    from odd.tools.registry import registry

    # 导入内置工具以触发自动注册
    from odd.tools.builtin import shell, filesystem, fetch_url, python  # noqa: F401

    # 创建模型
    if args.provider == "openai":
        from odd.models.openai import OpenAIProvider

        model = OpenAIProvider()
    else:
        from odd.models.anthropic import AnthropicProvider

        model = AnthropicProvider()

    tools = registry.list_tools()
    agent = Agent(model=model, tools=tools)

    print("🤖 Odd Agent 已就绪")
    print(f"   提供者: {args.provider}")
    print(f"   工具: {', '.join(t.spec.name for t in tools) or '无'}")
    print("   输入 'exit' 或 'quit' 退出\n")

    messages = None
    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("再见！")
            break

        try:
            result, messages = agent.chat(user_input, messages)
            print(result)
        except Exception as exc:
            print(f"[错误] {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
