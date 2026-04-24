"""验证阶段 2: 工具系统。

测试工具注册表、shell 执行、文件系统操作、网页获取和 Python 代码执行。
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odd.tools.registry import registry
from odd.tools.builtin.shell import ShellTool
from odd.tools.builtin.filesystem import FileSystemTool
from odd.tools.builtin.fetch_url import FetchUrlTool
from odd.tools.builtin.python import PythonTool


def test_registry():
    """在全局注册表中注册并检索工具。"""
    registry.clear()
    assert registry.list_tools() == []

    registry.register(ShellTool())
    registry.register(FileSystemTool())
    registry.register(FetchUrlTool())
    registry.register(PythonTool())

    assert registry.get("shell") is not None
    assert registry.get("filesystem") is not None
    assert registry.get("fetch_url") is not None
    assert registry.get("python") is not None
    assert len(registry.list_tools()) == 4
    print("[OK] Registry works")


def test_shell():
    """执行简单 shell 命令并验证输出。"""
    shell = ShellTool()
    result = shell.execute({"command": "echo hello"})
    data = json.loads(result)
    assert data["stdout"].strip() == "hello"
    assert data["returncode"] == 0
    print("[OK] Shell tool works")


def test_filesystem():
    """测试 write、read 和 list 操作。"""
    fs = FileSystemTool()

    # write
    r = fs.execute({"operation": "write", "path": "scripts/sandbox/test.txt", "content": "odd"})
    assert json.loads(r)["status"] == "ok"

    # read
    r = fs.execute({"operation": "read", "path": "scripts/sandbox/test.txt"})
    assert json.loads(r)["content"] == "odd"

    # list
    r = fs.execute({"operation": "list", "path": "scripts/sandbox"})
    entries = json.loads(r)["entries"]
    assert any(e["name"] == "test.txt" for e in entries)
    print("[OK] Filesystem tool works")


def test_fetch_url():
    """测试获取网页内容。"""
    fetch = FetchUrlTool()
    result = fetch.execute({"url": "https://httpbin.org/get"})
    data = json.loads(result)
    # httpbin 会返回 JSON，检查是否包含 url 字段
    assert "url" in data or "error" not in data
    print("[OK] Fetch URL tool works")


def test_python():
    """测试执行 Python 代码。"""
    py = PythonTool()

    # 表达式求值
    result = py.execute({"code": "1 + 2 + 3"})
    data = json.loads(result)
    assert data["result"] == "6"

    # 打印输出
    result = py.execute({"code": "print('hello from python tool')"})
    data = json.loads(result)
    assert "hello from python tool" in data["stdout"]
    print("[OK] Python tool works")


if __name__ == "__main__":
    test_registry()
    test_shell()
    test_filesystem()
    test_fetch_url()
    test_python()
    print("\nStage 2 verification complete.")
