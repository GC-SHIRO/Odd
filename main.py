"""Odd Agent 命令行交互入口。

启动后与 Agent 进行多轮对话，支持工具调用。
"""

import argparse
import json
import sys
from typing import Optional

import dotenv

# 若存在则加载 .env（本地开发时使用）。
dotenv.load_dotenv()


def _truncate(text: str, limit: int = 80) -> str:
    """截断文本并添加省略号。"""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def make_callbacks():
    """创建用于 CLI 的 think / tool_result 回调。"""

    def on_think(content: str, tool_calls, thinking: Optional[str]):
        # 优先使用模型原生的 thinking / reasoning_content
        if thinking:
            for line in thinking.splitlines():
                print(f"  💭 {_truncate(line, 120)}")
        else:
            # 退而求其次：尝试从文本内容中提取 <think> 标签
            if "<think>" in content and "</think>" in content:
                start = content.find("<think>") + len("<think>")
                end = content.find("</think>")
                think_text = content[start:end].strip()
                for line in think_text.splitlines():
                    print(f"  💭 {_truncate(line, 120)}")

        if tool_calls:
            for tc in tool_calls:
                args_str = json.dumps(tc.arguments, ensure_ascii=False)
                print(f"  🤔 调用工具: {tc.name}({_truncate(args_str)})")

    def on_tool_result(name: str, arguments: dict, result: str):
        # 尝试解析 JSON 结果，判断成功或失败
        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            data = None

        if isinstance(data, dict) and "error" in data:
            print(f"  ❌ 工具 [{name}] 错误: {data['error']}")
        else:
            # 简略显示结果（取第一行或前 60 字符）
            summary = result.replace("\n", " ").strip()
            print(f"  ✅ 工具 [{name}] 完成: {_truncate(summary, 60)}")

    return on_think, on_tool_result


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
    on_think, on_tool_result = make_callbacks()

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
            result, messages = agent.chat(
                user_input,
                messages,
                on_think=on_think,
                on_tool_result=on_tool_result,
            )
            print(result)
        except Exception as exc:
            print(f"[错误] {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
