"""文件系统读写工具。

提供文件读取、写入和目录列表功能。
"""

import json
from pathlib import Path
from typing import Any, Dict

from odd.tools.base import Tool, ToolSpec
from odd.tools.registry import register


class FileSystemTool(Tool):
    """读取或写入文件。"""

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="filesystem",
            description="读取、写入文件或列出目录内容。",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "list"],
                        "description": "要执行的操作。",
                    },
                    "path": {
                        "type": "string",
                        "description": "文件或目录路径。",
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的内容（write 时必需）。",
                    },
                },
                "required": ["operation", "path"],
            },
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        """执行请求的文件系统操作。"""
        operation = arguments.get("operation")
        path = arguments.get("path", "")
        target = Path(path)

        try:
            if operation == "read":
                if not target.exists():
                    return json.dumps({"error": "文件不存在"})
                if target.is_dir():
                    return json.dumps({"error": "路径是目录"})
                return json.dumps(
                    {"content": target.read_text(encoding="utf-8")},
                    ensure_ascii=False,
                )

            elif operation == "write":
                content = arguments.get("content", "")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                return json.dumps({"status": "ok", "bytes_written": len(content)})

            elif operation == "list":
                if not target.exists():
                    return json.dumps({"error": "路径不存在"})
                if not target.is_dir():
                    return json.dumps({"error": "路径不是目录"})
                entries = [
                    {"name": p.name, "type": "dir" if p.is_dir() else "file"}
                    for p in target.iterdir()
                ]
                return json.dumps({"entries": entries}, ensure_ascii=False)

            else:
                return json.dumps({"error": f"未知操作: {operation}"})
        except Exception as exc:
            return json.dumps({"error": str(exc)})


register(FileSystemTool())
