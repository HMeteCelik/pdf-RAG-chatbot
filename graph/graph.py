from graph.node_constants import RETRIEVE, GENERATE, GRADE_DOCUMENTS
from config import dprint
from graph.nodes import generate_node, grade_documents, retrieve_node
from graph.state import GraphState
from graph.chains.answer_grader import answer_grader
from graph.chains.hallucination_grader import hallucination_grader
from langgraph.graph import END, StateGraph, START

MAX_RETRIES = 3


def decide_to_generate(state: GraphState) -> str:
    if state["should_generate"]:
        return "supported"
    else:
        return "not supported"


def grade_generation(state: GraphState) -> str:
    retry_count = state.get("retry_count", 0)

    if retry_count >= MAX_RETRIES:
        dprint(f"---MAX RETRIES ({MAX_RETRIES}) REACHED, ACCEPTING GENERATION---")
        return "useful"

    if not state.get("should_generate", True):
        return "useful"

    dprint("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    dprint(f"---HALLUCINATION SCORE: {score.binary_score}---")

    if score.binary_score:
        dprint("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        dprint("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        dprint(f"---ANSWER SCORE: {score.binary_score}---")
        if score.binary_score:
            dprint("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            dprint("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        dprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS---")
        return "not supported"


workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE, retrieve_node)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate_node)


workflow.add_edge(START, RETRIEVE)

workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)

workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        "supported": GENERATE,
        "not supported": END,
    },
)

workflow.add_conditional_edges(
    GENERATE,
    grade_generation,
    {
        "useful": END,
        "not useful": GENERATE,
        "not supported": RETRIEVE,
    },
)

app = workflow.compile()
