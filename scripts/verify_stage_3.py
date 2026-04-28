"""验证阶段 3: Agent 核心循环。

测试 Agent 能否使用工具完成任务（包括模拟调用和真实 API 调用）。
"""

import json
import os
import sys
from unittest.mock import MagicMock
import dotenv
# 若存在则加载 .env（本地开发时使用）。
dotenv.load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odd.agent import Agent
from odd.models.base import ModelProvider
from odd.tools.builtin.shell import ShellTool
from odd.tools.builtin.filesystem import FileSystemTool
from odd.types import ChatResponse, Message, MessageRole, ToolCall


class FakeModel(ModelProvider):
    """模拟模型，按预设顺序返回响应。"""

    def __init__(self, responses: list):
        self.responses = responses
        self.call_idx = 0
        self.history: list = []

    def chat(self, messages, tools=None):
        self.history.append((messages, tools))
        resp = self.responses[self.call_idx]
        self.call_idx += 1
        return resp


def test_agent_no_tool():
    """Agent 不需要工具时直接返回答案。"""
    fake = FakeModel([ChatResponse(content="Hello, world!")])
    agent = Agent(model=fake, tools=[])
    result = agent.run("Say hello")
    assert result == "Hello, world!"
    print("[OK] Agent no-tool response works")


def test_agent_with_tool():
    """Agent 调用 shell 工具并返回结果。"""
    fake = FakeModel(
        [
            ChatResponse(
                content="",
                tool_calls=[ToolCall(id="tc1", name="shell", arguments={"command": "echo odd"})],
            ),
            ChatResponse(content="The result is odd"),
        ]
    )
    agent = Agent(model=fake, tools=[ShellTool()])
    result = agent.run("Run echo odd")
    assert "odd" in result
    # 验证工具结果确实被传回模型
    assert len(fake.history) == 2
    second_call_messages = fake.history[1][0]
    tool_msgs = [m for m in second_call_messages if m.role == MessageRole.TOOL]
    assert len(tool_msgs) == 1
    data = json.loads(tool_msgs[0].content)
    assert data["stdout"].strip() == "odd"
    print("[OK] Agent tool execution works")


def test_agent_max_rounds():
    """Agent 达到最大轮次后终止。"""
    # 每次都返回工具调用，永远不会结束
    fake = FakeModel(
        [
            ChatResponse(
                content="",
                tool_calls=[
                    ToolCall(id=f"tc{i}", name="shell", arguments={"command": "echo x"})
                ],
            )
            for i in range(15)
        ]
    )
    agent = Agent(model=fake, tools=[ShellTool()], max_rounds=3)
    result = agent.run("loop forever")
    assert "Maximum rounds reached" in result
    print("[OK] Agent max rounds limit works")


def test_agent_unknown_tool():
    """Agent 请求不存在的工具时返回错误。"""
    fake = FakeModel(
        [
            ChatResponse(
                content="",
                tool_calls=[ToolCall(id="tc1", name="nonexistent", arguments={})],
            ),
            ChatResponse(content="Got error"),
        ]
    )
    agent = Agent(model=fake, tools=[ShellTool()])
    result = agent.run("Call unknown tool")
    assert "Got error" in result
    tool_msgs = [m for m in fake.history[1][0] if m.role == MessageRole.TOOL]
    assert len(tool_msgs) == 1
    data = json.loads(tool_msgs[0].content)
    assert "not found" in data["error"]
    print("[OK] Agent unknown tool error works")


def test_agent_filesystem():
    """Agent 调用 filesystem 工具读写文件。"""
    fake = FakeModel(
        [
            ChatResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="tc1",
                        name="filesystem",
                        arguments={
                            "operation": "write",
                            "path": "scripts/sandbox/agent_test.txt",
                            "content": "agent was here",
                        },
                    )
                ],
            ),
            ChatResponse(content="File written successfully"),
        ]
    )
    agent = Agent(model=fake, tools=[FileSystemTool()])
    result = agent.run("Write a file")
    assert "successfully" in result
    print("[OK] Agent filesystem tool works")


def test_live_agent():
    """使用真实模型测试 Agent（需要 API key）。"""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("[SKIP] OPENAI_API_KEY not set, skipping live Agent test")
        return

    from odd.models.openai import OpenAIProvider

    provider = OpenAIProvider()
    agent = Agent(
        model=provider,
        tools=[ShellTool(), FileSystemTool()],
        max_rounds=5,
    )
    result = agent.run("Use the shell tool to echo 'Odd stage 3 ok' and tell me the output.")
    assert "stage 3 ok" in result.lower() or "Odd stage 3 ok" in result
    print(f"[OK] Live Agent response: {result.strip()}")


if __name__ == "__main__":
    test_agent_no_tool()
    test_agent_with_tool()
    test_agent_max_rounds()
    test_agent_unknown_tool()
    test_agent_filesystem()
    test_live_agent()
    print("\nStage 3 verification complete.")
