"""Shell 命令执行工具。

允许 Agent 执行 shell 命令，返回 stdout、stderr 和退出码。
"""

import json
import subprocess
from typing import Any, Dict

from odd.tools.base import Tool, ToolSpec
from odd.tools.registry import register


class ShellTool(Tool):
    """执行 shell 命令。"""

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="shell",
            description="执行 shell 命令，返回 stdout/stderr 和退出码。",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的 shell 命令。",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "最长等待秒数（默认 60）。",
                        "default": 60,
                    },
                },
                "required": ["command"],
            },
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        """运行命令并返回 JSON 编码的结果。"""
        command = arguments.get("command", "")
        timeout = arguments.get("timeout", 60)
        if not isinstance(command, str):
            return json.dumps({"error": "command 必须是字符串"})

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return json.dumps(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                },
                ensure_ascii=False,
            )
        except subprocess.TimeoutExpired:
            return json.dumps({"error": f"命令在 {timeout} 秒后超时"})
        except Exception as exc:
            return json.dumps({"error": str(exc)})


register(ShellTool())
