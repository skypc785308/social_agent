"""LangChain v1 agent setup with QSearch tools and conversation memory.

Uses the new `langchain.agents.create_agent` API (LangChain v1.2+)
with LangGraph MemorySaver for automatic conversation persistence.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from app.agent.tools import ALL_TOOLS
from app.agent.memory import get_checkpointer, make_thread_config

load_dotenv()

SYSTEM_PROMPT = """\
你是一位專業的輿情分析助手（Social Sentiment Analyst）。

你的職責是幫助使用者分析社群媒體上的網路聲量與輿情趨勢。

## 回答規則

- 使用**繁體中文**回答
- 在回答輿情相關問題前，**主動使用工具取得真實數據**，不要猜測或虛構數據
- 根據目前權限狀況，**不要嘗試使用聲量趨勢分析 (heatmap) 或 AI摘要 (summary) 的功能**
- 將數據整理成**易讀的格式**（表格、列表等）
- 數字使用**千分位格式**（如 1,234,567）
- 提供**關鍵洞察**，不只是列出數據
- 若使用者的問題不涉及輿情分析，仍可友善地回答一般問題
"""


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def _create_agent():
    """Create a LangChain v1 agent with tools, memory, and system prompt."""
    llm = _get_llm()
    checkpointer = get_checkpointer()

    agent = create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
    return agent


# Singleton agent (the graph is stateless; state lives in the checkpointer)
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = _create_agent()
    return _agent


async def chat(session_id: str, message: str) -> str:
    """Send a message to the agent and return its response.

    Uses thread_id-based memory for automatic conversation continuity.

    Args:
        session_id: Unique session identifier for memory isolation.
        message: User's input message.

    Returns:
        Agent's text response.
    """
    agent = get_agent()
    config = make_thread_config(session_id)

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )

    # Extract the last AI message content
    messages = result["messages"]
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content and msg.type == "ai":
            return msg.content

    return "抱歉，我無法處理您的請求。請再試一次。"
