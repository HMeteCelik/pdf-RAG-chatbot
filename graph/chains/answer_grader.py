from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm import llm


class CheckAnswer(BaseModel):
    """
    Binary score whether the answer addresses the question.
    """
    binary_score: bool = Field(
        description="True if the answer adequately addresses the question, False otherwise."
    )


structured_llm = llm.with_structured_output(CheckAnswer)

system_prompt = """You are a grader assessing whether an answer adequately addresses or resolves a given question.

Evaluate based on the following criteria:
- Does the answer directly respond to what was asked?
- Is the information relevant to the question topic?
- Does the answer provide a meaningful response (not evasive or empty)?

Important rules:
- The answer and question may be in ANY language (Turkish, English, etc.). Evaluate the semantic meaning regardless of language.
- If the answer contains relevant information about the question topic, grade it as True.
- Only grade as False if the answer is completely off-topic, nonsensical, or does not address the question at all.
- Be lenient: partial but relevant answers should be graded as True.

Return True if the answer addresses the question, False otherwise."""

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', system_prompt),
        ('human', 'User question:\n{question}\n\nLLM generation:\n{generation}')
    ]
)

answer_grader = answer_prompt | structured_llm