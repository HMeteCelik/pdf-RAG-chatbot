from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm import llm


class HallucinationGrader(BaseModel):
    """Binary score for hallucination present in generated answer."""
    binary_score: bool = Field(
        description="True if the generation is grounded in and supported by the provided facts, False otherwise."
    )


structured_llm = llm.with_structured_output(HallucinationGrader)

hallucination_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a grader assessing whether an LLM generation is grounded in and supported by a set of retrieved facts.

Important rules:
- The generation and facts may be in ANY language (Turkish, English, etc.). Evaluate semantic meaning regardless of language.
- If the generation conveys information that is consistent with the provided facts, grade it as True.
- Only grade as False if the generation contains claims that clearly contradict or are not supported by any of the provided facts.
- Be lenient: the generation does not need to use the exact same words as the facts.

Return True if the generation is grounded in the facts, False otherwise."""),
    ("human",
     "Set of facts:\n\n{documents}\n\nLLM generation:\n{generation}")
])

hallucination_grader = hallucination_prompt | structured_llm