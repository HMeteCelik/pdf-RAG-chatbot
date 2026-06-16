from graph.chains.generation import generator
from config import dprint
from graph.state import GraphState
from langchain_core.messages import HumanMessage, AIMessage
from typing import Any, Dict


def generate_node(state: GraphState) -> Dict[str, Any]:
    dprint("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    should_generate = state.get("should_generate", True)
    retry_count = state.get("retry_count", 0)
    chat_history = state.get("chat_history", [])

    if not should_generate:
        return {
            "question": question,
            "documents": documents,
            "generation": "There is no information in the given document that addresses your question.",
            "retry_count": retry_count,
        }

    history_messages = []
    for human_msg, ai_msg in chat_history:
        history_messages.append(HumanMessage(content=human_msg))
        history_messages.append(AIMessage(content=ai_msg))

    generation = generator.invoke(
        {'context': documents, 'question': question, 'chat_history': history_messages}
    )
    dprint(generation)
    return {
        "question": question,
        "documents": documents,
        "generation": generation,
        "retry_count": retry_count + 1,
    }