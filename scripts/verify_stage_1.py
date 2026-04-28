"""验证阶段 1：模型调用层。"""

import os
from dotenv import load_dotenv
import sys

# 若存在则加载 .env（本地开发时使用）。
load_dotenv()
# 允许从仓库根目录导入 odd。
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from odd.types import Message, MessageRole, ToolCall
from odd.config import Config
from odd.models.base import ModelProvider
from odd.models.openai import OpenAIProvider
from odd.models.anthropic import AnthropicProvider


def test_imports():
    print("[OK] Imports successful")


def test_types():
    msg = Message(role=MessageRole.USER, content="Hello")
    assert msg.role == MessageRole.USER
    assert msg.content == "Hello"

    tc = ToolCall(id="1", name="test", arguments={"a": 1})
    assert tc.name == "test"

    print("[OK] Types work")


def test_config():
    cfg = Config.from_env()
    assert cfg.default_provider in ("openai", "anthropic")
    print(f"[OK] Config loaded (default_provider={cfg.default_provider})")


def test_openai_mock():
    """测试 OpenAI 提供者实例化（不发起真实调用）。"""
    try:
        provider = OpenAIProvider()
        assert isinstance(provider, ModelProvider)
        print("[OK] OpenAIProvider instantiates")
    except ImportError:
        print("[SKIP] openai package not installed")


def test_anthropic_mock():
    """测试 Anthropic 提供者实例化（不发起真实调用）。"""
    try:
        provider = AnthropicProvider()
        assert isinstance(provider, ModelProvider)
        print("[OK] AnthropicProvider instantiates")
    except ImportError:
        print("[SKIP] anthropic package not installed")


def test_openai_chat():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("[SKIP] OPENAI_API_KEY not set, skipping live OpenAI call")
        return

    provider = OpenAIProvider()
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a concise assistant."),
        Message(role=MessageRole.USER, content="Say 'Odd stage 1 ok' and nothing else."),
    ]
    resp = provider.chat(messages)
    assert "stage 1 ok" in resp.content.lower()
    print(f"[OK] OpenAI live response: {resp.content.strip()}")


def test_anthropic_chat():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        print("[SKIP] ANTHROPIC_API_KEY not set, skipping live Anthropic call")
        return

    provider = AnthropicProvider()
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a concise assistant."),
        Message(role=MessageRole.USER, content="Say 'Odd stage 1 ok' and nothing else."),
    ]
    resp = provider.chat(messages)
    assert "stage 1 ok" in resp.content.lower()
    print(f"[OK] Anthropic live response: {resp.content.strip()}")


if __name__ == "__main__":
    test_imports()
    test_types()
    test_config()
    test_openai_mock()
    test_anthropic_mock()
    test_openai_chat()
    test_anthropic_chat()
    print("\nStage 1 verification complete.")
