"""Session-based conversation memory using LangGraph InMemorySaver.

In LangChain v1, conversation memory is handled by LangGraph's checkpointer.
Each session is identified by a `thread_id` in the config, and the InMemorySaver
automatically persists and retrieves conversation state per thread.
"""

from langgraph.checkpoint.memory import InMemorySaver

# Singleton in-memory checkpointer — stores all sessions automatically
_checkpointer = InMemorySaver()


def get_checkpointer() -> InMemorySaver:
    """Get the shared InMemorySaver instance."""
    return _checkpointer


def make_thread_config(session_id: str) -> dict:
    """Create a LangGraph config with thread_id for session isolation.

    Args:
        session_id: Unique session identifier.

    Returns:
        Config dict with {"configurable": {"thread_id": session_id}}.
    """
    return {"configurable": {"thread_id": session_id}}


def reset_memory(session_id: str) -> None:
    """Reset conversation memory for a session by replacing the checkpointer.

    Note: MemorySaver stores data in a dict. We delete the thread's storage
    to effectively reset it. On next invocation, a fresh thread starts.
    """
    # MemorySaver uses an internal storage dict; clear the specific thread
    storage = _checkpointer.storage
    keys_to_delete = [k for k in storage if k[0] == session_id]
    for key in keys_to_delete:
        del storage[key]
