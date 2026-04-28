"""Agent 核心：ReAct 循环。

实现 思考 -> 行动 -> 观察 的循环，让 Agent 能自主使用工具完成任务。
"""

import json
from typing import List, Optional

from odd.models.base import ModelProvider
from odd.tools.base import Tool
from odd.types import ChatResponse, Message, MessageRole, ToolCall


class Agent:
    """具备工具使用能力的 ReAct Agent。"""

    def __init__(
        self,
        model: ModelProvider,
        tools: Optional[List[Tool]] = None,
        max_rounds: int = 10,
        system_prompt: Optional[str] = None,
    ):
        self.model = model
        self.tools = tools or []
        self.max_rounds = max_rounds
        self.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        lines = [
            "You are Odd, a helpful assistant that can use tools to solve tasks.",
            "",
            "Available tools:",
        ]
        for tool in self.tools:
            spec = tool.spec
            lines.append(f"- {spec.name}: {spec.description}")
            lines.append(
                f"  Parameters: {json.dumps(spec.parameters, ensure_ascii=False)}"
            )
        lines.append("")
        lines.append(
            "When you need to use a tool, the system will automatically process your request."
        )
        lines.append("If no tool is needed, simply respond with your answer.")
        return "\n".join(lines)

    def run(
        self,
        task: str,
        on_think: Optional[callable] = None,
        on_tool_result: Optional[callable] = None,
    ) -> str:
        """为给定任务执行 ReAct 循环。

        Args:
            task: The user's task description.
            on_think: Callback(content, tool_calls, thinking) fired after each model response.
            on_tool_result: Callback(name, arguments, result) fired after each tool execution.

        Returns:
            The final answer from the model.
        """
        messages: List[Message] = [
            Message(role=MessageRole.SYSTEM, content=self.system_prompt),
            Message(role=MessageRole.USER, content=task),
        ]
        return self._react_loop(messages, on_think=on_think, on_tool_result=on_tool_result)

    def chat(
        self,
        user_input: str,
        messages: Optional[List[Message]] = None,
        on_think: Optional[callable] = None,
        on_tool_result: Optional[callable] = None,
    ) -> tuple[str, List[Message]]:
        """执行一轮保留上下文的对话。

        Args:
            user_input: The user's message.
            messages: Existing conversation history. If None, a new session starts.
            on_think: Callback(content, tool_calls, thinking) fired after each model response.
            on_tool_result: Callback(name, arguments, result) fired after each tool execution.

        Returns:
            A tuple of (final_answer, updated_messages).
        """
        if messages is None:
            messages = [
                Message(role=MessageRole.SYSTEM, content=self.system_prompt),
            ]
        messages.append(Message(role=MessageRole.USER, content=user_input))
        result = self._react_loop(
            messages, on_think=on_think, on_tool_result=on_tool_result
        )
        return result, messages

    def _react_loop(
        self,
        messages: List[Message],
        on_think: Optional[callable] = None,
        on_tool_result: Optional[callable] = None,
    ) -> str:
        """ReAct 核心循环。原地修改 *messages* 列表。"""
        for _ in range(self.max_rounds):
            api_tools = [_to_api_tool(t) for t in self.tools] if self.tools else None
            response: ChatResponse = self.model.chat(messages, tools=api_tools)

            if on_think:
                on_think(response.content, response.tool_calls, response.thinking)

            # 没有工具调用时，认为任务完成
            if not response.tool_calls:
                return response.content

            # 将 assistant 的回复（含工具调用）加入上下文
            messages.append(
                Message(
                    role=MessageRole.ASSISTANT,
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            # 执行每个工具调用，并将结果追加回上下文
            for tc in response.tool_calls:
                tool = self._find_tool(tc.name)
                if tool is None:
                    result = json.dumps(
                        {"error": f"Tool '{tc.name}' not found"}, ensure_ascii=False
                    )
                else:
                    try:
                        result = tool.execute(tc.arguments)
                    except Exception as exc:
                        result = json.dumps(
                            {"error": str(exc)}, ensure_ascii=False
                        )

                if on_tool_result:
                    on_tool_result(tc.name, tc.arguments, result)

                messages.append(
                    Message(
                        role=MessageRole.TOOL,
                        content=result,
                        tool_call_id=tc.id,
                        name=tc.name,
                    )
                )

        return "Maximum rounds reached without completion."

    def _find_tool(self, name: str) -> Optional[Tool]:
        for t in self.tools:
            if t.spec.name == name:
                return t
        return None


def _to_api_tool(tool: Tool) -> dict:
    """将内部 Tool 转换为 OpenAI 兼容的 API 格式。"""
    spec = tool.spec
    return {
        "type": "function",
        "function": {
            "name": spec.name,
            "description": spec.description,
            "parameters": spec.parameters,
        },
    }
