# 阶段 3：Agent 核心循环

## 一句话总结

**Agent 核心循环 = 把"嘴巴耳朵"和"手脚"串起来的"大脑皮层"**。它让模型能够**反复思考→调用工具→观察结果→再思考**，直到任务完成。

---

## 前两个阶段各自为战，现在要把它们连起来

- 阶段 1 的模型层：会"聊天"，但聊完就完了
- 阶段 2 的工具系统：会"干活"，但没人指挥它

Agent 核心循环就是那个**指挥官**：
1. 把用户任务告诉模型
2. 模型思考后说"我需要用某某工具"
3. Agent 找到这个工具，执行它
4. 把执行结果塞回对话历史
5. 模型看到结果，继续思考下一步
6. 重复直到模型说"搞定了"

这就是大名鼎鼎的 **ReAct 循环**（Reason → Act → Observe）。

---

## 核心零件

### 1. Agent 类（`odd/agent.py`）

Agent 是这一切的 orchestrator（ orchestrator 是"总指挥"的意思）。它身上挂着两样东西：

```python
class Agent:
    def __init__(self, model, tools, max_rounds=10):
        self.model = model      # ← 阶段 1 的模型
        self.tools = tools      # ← 阶段 2 的工具列表
```

#### `run(task)` 主循环

这是 Agent 的心脏，代码逻辑可以翻译成大白话：

```
用户：帮我查一下当前目录有什么文件

第 1 轮：
  → 把任务丢给模型
  ← 模型说："我要用 shell 工具执行 ls"
  → Agent 执行 shell("ls")
  → 结果：['agent.py', 'config.py', ...]

第 2 轮：
  → 把结果再丢给模型
  ← 模型说："当前目录有 agent.py、config.py..."
  → 模型没有请求工具 → **任务完成，返回答案**
```

代码里就是一个 `for` 循环，最多跑 `max_rounds` 轮（默认 10 轮），防止模型陷入死循环。

#### System Prompt 的构建

模型怎么知道"你有这些工具可以用"？靠 **system prompt**。

Agent 在启动时自动拼接一段系统提示，告诉模型：
- 你是谁（你是一个叫 Odd 的 Agent）
- 你有什么工具（shell、filesystem...）
- 每个工具需要传什么参数

```
You are Odd, a helpful assistant...

Available tools:
- shell: 执行 shell 命令...
  Parameters: {"type": "object", "properties": {"command": ...}}
- filesystem: 读写文件...
  Parameters: {"type": "object", ...}
```

#### 消息历史的维护

每次循环，Agent 都要把**之前所有的对话**一起发给模型。这包括：
1. System prompt（告诉模型规则）
2. User 的原始任务
3. Assistant 说"我要调用工具 X"
4. Tool 返回的执行结果
5. Assistant 的新回复
6. ...

这个过程就像你和一个健忘的朋友聊天——每轮都必须把**全部聊天记录**转发给他，否则他会忘之前说过什么。

---

### 2. 工具调用在模型层的新变化

阶段 1 的模型只会"聊天"。现在要让模型**主动决定用不用工具**，所以给 `chat()` 方法加了一个 `tools` 参数：

```python
# Agent 调用模型时，把可用工具的定义也传进去
response = model.chat(messages, tools=api_tools)
```

OpenAI 和 Anthropic 的 API 都支持这种方式：你传工具定义，模型自己判断要不要调用。

#### 两种 API 的工具格式差异

虽然 Agent 统一用 OpenAI 格式传工具，但 Anthropic 的 API 格式不一样，需要在 AnthropicProvider 里做转换：

| 字段 | OpenAI 格式 | Anthropic 格式 |
|------|------------|---------------|
| 类型 | `type: "function"` | 没有外层 type |
| 名字 | `function.name` | `name` |
| 参数 | `function.parameters` | `input_schema` |

```python
# OpenAI 格式
tools = [{
    "type": "function",
    "function": {
        "name": "shell",
        "description": "执行 shell 命令",
        "parameters": {...}
    }
}]

# Anthropic 格式（内部转换后）
tools = [{
    "name": "shell",
    "description": "执行 shell 命令",
    "input_schema": {...}
}]
```

---

### 3. 踩过的坑：`str()`  vs `json.dumps()`

在实现过程中遇到一个隐蔽的 Bug。

Agent 收到模型的 tool_calls 后，要把它们**原封不动地塞回消息历史**，再发给模型。这一步在 `_to_openai_msg()` 里做转换。

一开始写的是：

```python
"arguments": str(tc.arguments)  # tc.arguments 是字典 {"command": "ls"}
```

结果 API 报错：`invalid function arguments json string`

**原因**：`str({"command": "ls"})` 得到的是 Python 字典的字符串表示 `'{"command": "ls"}'`？不，实际上得到的是 `"{'command': 'ls'}"`——**单引号**！而 JSON 标准必须用**双引号**。

正确的做法是：

```python
"arguments": json.dumps(tc.arguments)  # 得到 '{"command": "ls"}'
```

**教训**：和外部 API 打交道时，数据序列化一定要用标准的 `json.dumps()`，不要用 Python 的 `str()`。

---

## 验证方式

运行 `python scripts/verify_stage_3.py`，它会测试：

1. **无工具场景**：模型直接回答，Agent 一次循环就结束
2. **工具调用场景**：模型请求调用 shell 工具，Agent 执行后把结果回传
3. **最大轮次限制**：模型一直请求工具，Agent 跑到 `max_rounds` 后强制终止
4. **未知工具**：模型请求了一个不存在的工具，Agent 返回错误信息
5. **真实 API 调用**：如果有 API Key，真的会发请求给模型，让它用 shell 工具执行命令

---

## 学到的要点

1. **ReAct 是 Agent 的 DNA**：没有"思考→行动→观察"的循环，模型只是一个聊天机器人，不是 Agent。
2. **消息历史是状态**：Agent 的"记忆"就是对话历史，每轮都要完整传给模型。
3. **终止条件很重要**：没有终止条件，模型可能无限循环调用工具。我们用了两种终止：模型不再请求工具、达到最大轮次。
4. **数据格式是暗礁**：和 API 交互时，`str()` 和 `json.dumps()` 看起来差不多，实际上天差地别。
5. **抽象分层的好处**：阶段 3 只负责"编排循环"，具体怎么聊天（阶段 1）和怎么执行工具（阶段 2）完全不用关心。每层只做好自己的事。
