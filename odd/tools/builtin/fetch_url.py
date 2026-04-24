"""URL 内容获取工具。

允许 Agent 获取网页内容。
"""

import json
from typing import Any, Dict
from urllib import request, error

from odd.tools.base import Tool, ToolSpec
from odd.tools.registry import register


class FetchUrlTool(Tool):
    """获取指定 URL 的内容。"""

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="fetch_url",
            description="获取指定 URL 的网页内容。",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要获取的 URL 地址。",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "请求超时秒数（默认 30）。",
                        "default": 30,
                    },
                },
                "required": ["url"],
            },
        )

    def execute(self, arguments: Dict[str, Any]) -> str:
        """获取 URL 内容。"""
        url = arguments.get("url", "")
        timeout = arguments.get("timeout", 30)
        if not isinstance(url, str):
            return json.dumps({"error": "url 必须是字符串"})

        try:
            req = request.Request(url, headers={"User-Agent": "Odd-Agent/0.1"})
            with request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                # 尝试按 UTF-8 解码，失败则保持原始字节
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = data.decode("utf-8", errors="replace")
                return json.dumps(
                    {
                        "status": resp.status,
                        "url": resp.geturl(),
                        "content": text,
                    },
                    ensure_ascii=False,
                )
        except error.HTTPError as exc:
            return json.dumps({"error": f"HTTP {exc.code}: {exc.reason}"})
        except error.URLError as exc:
            return json.dumps({"error": f"URL 错误: {exc.reason}"})
        except Exception as exc:
            return json.dumps({"error": str(exc)})


register(FetchUrlTool())
