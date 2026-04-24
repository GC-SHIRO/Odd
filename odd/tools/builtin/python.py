"""Python 代码执行工具。

允许 Agent 执行 Python 代码片段，返回输出结果。
"""

import io
import json
import sys
import traceback
from typing import Any, Dict

from odd.tools.base import Tool, ToolSpec
from odd.tools.registry import register


class PythonTool(Tool):
    """执行 Python 代码片段。"""

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="python",
            description="执行 Python 代码片段，返回 stdout 和最后一个表达式的值。",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的 Python 代码。",
                    },
                },
                "required": ["code"],
            },
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        """执行 Python 代码并捕获输出。"""
        code = arguments.get("code", "")
        if not isinstance(code, str):
            return json.dumps({"error": "code 必须是字符串"})

        # 重定向 stdout 和 stderr 以捕获输出
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer

        try:
            # 先尝试作为表达式求值（如 1+1）
            try:
                result = eval(code, {"__builtins__": __builtins__}, {})
            except SyntaxError:
                # 语法错误说明是语句块，用 exec 执行
                exec(code, {"__builtins__": __builtins__}, {})
                result = None

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            return json.dumps(
                {
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue(),
                    "result": repr(result) if result is not None else None,
                },
                ensure_ascii=False,
            )
        except Exception:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            return json.dumps(
                {
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue() + traceback.format_exc(),
                    "result": None,
                },
                ensure_ascii=False,
            )


register(PythonTool())
