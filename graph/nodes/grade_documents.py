from typing import Dict, Any
from graph.chains.retrieval_grader import retrieval_grader
from graph.state import GraphState
from config import dprint

def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question.
    If any document is not relevant, it is filtered out.
    Sets the 'generate' flag based on whether any relevant documents remain.

    Args:
        state (dict): The current state of the graph

    """

    question = state["question"]
    documents = state["documents"]
    filtered_documents = []
    for d in documents:
        dprint(d)
        score = retrieval_grader.invoke(
            {"question": question, "document": d}
        )

        grade = score.binary_score

        if grade.lower() == "yes":
            dprint("---GRADE: YES---")
            filtered_documents.append(d)
        else:
            dprint("---GRADE: NO---")

    should_generate = len(filtered_documents) > 0

    return {
        "question": question,
        "documents": filtered_documents,
        "should_generate": should_generate,
    }