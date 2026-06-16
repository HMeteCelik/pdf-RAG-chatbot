from typing import List, Tuple, TypedDict


class GraphState(TypedDict):
    """
    Respresents the state of the graph
    Attributes:
        question: question
        generation: LLM Generation
        documents: list of documents
        should_generate: whether to generate an answer
        retry_count: number of generation retries
        chat_history: list of (human, ai) message tuples
    """
    question: str
    generation: str
    documents: List[str]
    should_generate: bool
    retry_count: int
    chat_history: List[Tuple[str, str]]