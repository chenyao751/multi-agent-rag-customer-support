from typing import Optional
from langchain_core.runnables import Runnable, RunnableConfig
from customer_support_chat.app.core.state import State
from pydantic import BaseModel
from customer_support_chat.app.core.settings import get_settings
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

settings = get_settings()

# Initialize the language model (shared among assistants)
llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    openai_api_key=settings.OPENAI_API_KEY,
    openai_api_base=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None,
    temperature=1,
    max_tokens=settings.MAX_TOKENS,  # Limit tokens to control costs
)

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: Optional[RunnableConfig] = None):
        from customer_support_chat.app.core.logger import logger

        # 日志：记录调用前的消息状态
        logger.info(f"🤖 Assistant called with {len(state.get('messages', []))} messages")
        for i, msg in enumerate(state.get('messages', [])):
            msg_type = type(msg).__name__
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                logger.info(f"🤖   Message {i}: {msg_type} with tool_calls {[tc['id'] for tc in msg.tool_calls]}")
            elif hasattr(msg, 'tool_call_id'):
                logger.info(f"🤖   Message {i}: {msg_type} responding to {msg.tool_call_id}")
            else:
                content_preview = str(msg.content)[:50] if hasattr(msg, 'content') else "no content"
                logger.info(f"🤖   Message {i}: {msg_type} - {content_preview}")

        while True:
            result = self.runnable.invoke(state, config)

            # 日志：记录返回的消息
            logger.debug(f"Assistant returned message type: {type(result).__name__}")
            if hasattr(result, 'tool_calls'):
                logger.debug(f"Result has {len(result.tool_calls)} tool_calls: {[tc['id'] for tc in result.tool_calls]}")

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

# Define the CompleteOrEscalate tool
@tool
def CompleteOrEscalate(reason: str) -> str:
    """A tool to mark the current task as completed or to escalate control to the main assistant.
    
    Args:
        reason: Reason for completion or escalation
        
    Returns:
        A message confirming the action
    """
    return f"Task completed/escalated to main assistant. Reason: {reason}"