from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from llm import llm

class GradeDocuments(BaseModel):
    """
    Binary score for relevance check on retrieved documents.
    """
    binary_score: str = Field(description="'yes' or 'no'")


structured_llm = llm.with_structured_output(GradeDocuments)

grade_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a grader assessing whether a retrieved document contains information 
        \nRELEVANT to answering the user's question.

        \nIMPORTANT RULES:
        \n- Grade YES if the document contains ANY information related to the question topic
        \n- Grade YES even if the answer is partial or embedded within other content  
        \n- Grade NO only if the document is COMPLETELY unrelated to the question
        \n- Do NOT require the document to directly and explicitly answer the question

        \nRetrieved document:
        \n{document}

        \nUser question: {question}

        \nGive a binary score 'YES' or 'NO':"""),
    ("human",
     "Retrieved document: {document}\nQuestion: {question}")
])

retrieval_grader = grade_prompt | structured_llm