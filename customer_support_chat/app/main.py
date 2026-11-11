# main.py

import uuid
import os  # Import os module for file operations
from customer_support_chat.app.graph import multi_agentic_graph
from customer_support_chat.app.services.utils import download_and_prepare_db
from customer_support_chat.app.core.logger import logger
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage

# Import guardrail agents
from customer_support_chat.app.services.guardrails.guardrail_agents import (
    jailbreak_guardrail_agent,
    relevance_guardrail_agent,
    jailbreak_guardrail_agent_instructions,
    relevance_guardrail_agent_instructions,
)


def check_guardrails(user_input: str) -> tuple[bool, str]:
    """Check if user input passes safety and relevance guardrails.

    Args:
        user_input: The user's input text

    Returns:
        Tuple of (is_safe, message). If is_safe is False, message contains the rejection reason.
    """
    logger.info(f"🛡️ Checking guardrails for: '{user_input}'")

    # 1. Check for jailbreak attempts
    try:
        jailbreak_prompt = f"{jailbreak_guardrail_agent_instructions}\n\nUser Input: {user_input}"
        jailbreak_result = jailbreak_guardrail_agent.invoke([
            {"role": "user", "content": jailbreak_prompt}
        ])

        if not jailbreak_result.is_safe:
            logger.warning(f"🚨 Jailbreak attempt detected: {jailbreak_result.reasoning}")
            return False, f"I cannot assist with that request. Reason: {jailbreak_result.reasoning}"

    except Exception as e:
        logger.error(f"Jailbreak check failed: {e}. Allowing by default.")

    # 2. Check for relevance
    try:
        relevance_prompt = f"{relevance_guardrail_agent_instructions}\n\nUser Input: {user_input}"
        relevance_result = relevance_guardrail_agent.invoke([
            {"role": "user", "content": relevance_prompt}
        ])

        if not relevance_result.is_relevant:
            logger.warning(f"⚠️ Irrelevant query detected: {relevance_result.reasoning}")
            return False, "I'm sorry, but your query appears to be outside my area of expertise. I specialize in travel-related queries such as flights, hotels, car rentals, and excursions. Please ask me something related to these topics."

    except Exception as e:
        logger.error(f"Relevance check failed: {e}. Allowing by default.")

    logger.info("✅ Input passed guardrail checks")
    return True, ""

def main():
    # Ensure the database is downloaded and prepared
    download_and_prepare_db()

    # Generate and save the graph visualization
    try:
        # Generate the graph object with xray=True to include node details
        graph = multi_agentic_graph.get_graph(xray=True)
        # Draw the graph as a PNG image using Mermaid
        graph_image = graph.draw_mermaid_png()
        graphs_dir = "./graphs"
        if not os.path.exists(graphs_dir):
            os.makedirs(graphs_dir)
        image_path = os.path.join(graphs_dir, "multi-agent-rag-system-graph.png")
        with open(image_path, "wb") as f:
            f.write(graph_image)
        print(f"Graph saved at {image_path}")
    except Exception as e:
        logger.error(f"An error occurred while generating the graph visualization: {e}")
        print("Graph visualization could not be generated. Continuing without it.")

    # Generate a unique thread ID for the session
    thread_id = str(uuid.uuid4())

    # Configuration with passenger_id and thread_id
    config = {
        "configurable": {
            "passenger_id": "5102 899977",  # Update with a valid passenger ID as needed
            "thread_id": thread_id,
        }
    }

    # Variable to track printed message IDs to avoid duplicates
    printed_message_ids = set()

    try:
        while True:
            user_input = input("User: ")
            if user_input.strip().lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            # Pre-filter: Check guardrails BEFORE entering the graph
            is_safe, rejection_message = check_guardrails(user_input)
            if not is_safe:
                # Print rejection message directly, don't enter the graph
                print(f"\n{rejection_message}\n")
                continue

            # Process the user input through the graph (use invoke instead of stream)
            result = multi_agentic_graph.invoke(
                {"messages": [("user", user_input)]}, config
            )

            # Display all messages from the result
            messages = result.get("messages", [])
            for message in messages:
                if message.id not in printed_message_ids:
                    message.pretty_print()
                    printed_message_ids.add(message.id)

            # Check for interrupts
            snapshot = multi_agentic_graph.get_state(config)
            while snapshot.next:
                # Interrupt occurred before sensitive tool execution
                user_input = input(
                    "\nDo you approve of the above actions? Type 'y' to continue; otherwise, explain your requested changes.\n\n"
                )
                if user_input.strip().lower() == "y":
                    # Continue execution
                    result = multi_agentic_graph.invoke(None, config)
                else:
                    # Provide feedback to the assistant
                    tool_call_id = snapshot.value["messages"][-1].tool_calls[0]["id"]
                    result = multi_agentic_graph.invoke(
                        {
                            "messages": [
                                ToolMessage(
                                    tool_call_id=tool_call_id,
                                    content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
                                )
                            ]
                        },
                        config,
                    )
                # Process the result to display any new messages
                messages = result.get("messages", [])
                for message in messages:
                    if message.id not in printed_message_ids:
                        message.pretty_print()
                        printed_message_ids.add(message.id) 
                        
                # Update the snapshot
                snapshot = multi_agentic_graph.get_state(config)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print("An unexpected error occurred. Please check the logs for more details.")

if __name__ == "__main__":
    main()
