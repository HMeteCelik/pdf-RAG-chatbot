import vector_db
from graph.state import GraphState
from typing import Dict, Any
from config import dprint

def retrieve_node(state: GraphState) -> Dict[str, Any]:
    dprint("---RETRIEVE---")
    question = state["question"]
    documents = vector_db.retriever.invoke(question)

    return {"question": question, "documents": documents}
